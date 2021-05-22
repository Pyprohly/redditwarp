
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Optional, Mapping, MutableMapping, MutableSequence
    from ..http.session_base_SYNC import SessionBase
    from .authorizer_SYNC import Authorizer, Authorized
    from ..http.response import Response
    from ..http.requestor_SYNC import Requestor

import sys
import collections

from .. import __about__
from .. import auth
from .. import http
from ..auth.exceptions import raise_for_resource_server_response
from .exceptions import handle_auth_response_exception
from ..http.request import Request
from ..http.http_client_base_SYNC import HTTPClientBase
from ..http.transport.SYNC import get_session_underlying_library_name_and_version

class RedditHTTPClient(HTTPClientBase):
    DEFAULT_PARAMS: Mapping[str, str] = {
        'raw_json': '1',
        'api_type': 'json',
    }

    @property
    def user_agent(self) -> str:
        return self.headers['User-Agent']

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        self.headers['User-Agent'] = value

    @property
    def authorizer(self) -> Optional[Authorizer]:
        if self.authorized_requestor is None:
            return None
        return self.authorized_requestor.authorizer

    @authorizer.setter
    def authorizer(self, value: Authorizer) -> None:
        if self.authorized_requestor is None:
            raise RuntimeError('The client is not configured in a way that knows how to update this field.')
        self.authorized_requestor.authorizer = value

    def __init__(self,
        session: SessionBase,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        params = dict(self.DEFAULT_PARAMS) if params is None else params
        super().__init__(session, params=params, headers=headers)
        self.requestor: Requestor = session
        self.authorized_requestor: Optional[Authorized] = None
        self.user_agent = self.user_agent_start = get_http_client_user_agent(session)
        self.last_response: Optional[Response] = None
        self.last_response_queue: MutableSequence[Response] = collections.deque(maxlen=12)

    def send(self,
        request: Request,
        timeout: float = -2,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        try:
            resp = self.requestor.send(request, timeout=timeout, aux_info=aux_info)
        except (
            auth.exceptions.ResponseException,
            http.exceptions.ResponseException,
        ) as e:
            resp = e.response
            self.last_response = resp
            self.last_response_queue.append(resp)

            if isinstance(e, auth.exceptions.ResponseException):
                raise handle_auth_response_exception(e)
            raise

        self.last_response = resp
        self.last_response_queue.append(resp)

        raise_for_resource_server_response(resp)
        return resp


def get_http_client_user_agent(session: object) -> str:
    transport_name, transport_version = get_session_underlying_library_name_and_version(session)
    py_version = '.'.join(map(str, sys.version_info[:2]))
    return (
        f"{__about__.__title__}/{__about__.__version__} "
        f"Python/{py_version} "
        f"{transport_name}/{transport_version}"
    )
