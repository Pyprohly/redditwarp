
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Optional, Mapping, MutableMapping, MutableSequence
    from ..http.base_session_SYNC import BaseSession
    from .authorizer_SYNC import Authorizer, Authorized
    from ..http.response import Response

import sys
from collections import deque

from .. import __about__
from .. import auth
from .. import http
from ..auth.exceptions import raise_for_resource_server_response
from .exceptions import handle_auth_response_exception
from ..http.request import Request
from ..http.base_http_client_SYNC import BaseHTTPClient

class RedditHTTPClient(BaseHTTPClient):
    TIMEOUT = 8
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
        session: BaseSession,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        params = dict(self.DEFAULT_PARAMS) if params is None else params
        super().__init__(session, params=params, headers=headers)
        self.authorized_requestor: Optional[Authorized] = None
        self.user_agent = self.user_agent_string_head = (
            f"{__about__.__title__}/{__about__.__version__} "
            f"Python/{'.'.join(map(str, sys.version_info[:2]))} "
            f"{session.TRANSPORTER_INFO.name}/{session.TRANSPORTER_INFO.version}"
        )
        self.last_response: Optional[Response] = None
        self.last_response_queue: MutableSequence[Response] = deque(maxlen=12)

    def send(self,
        request: Request,
        timeout: float = TIMEOUT,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        try:
            resp = super().send(request, timeout=timeout, aux_info=aux_info)
        except (
            auth.exceptions.ResponseException,
            http.exceptions.ResponseException,
        ) as e:
            resp = e.response
            self.last_response = resp
            self.last_response_queue.append(resp)

            if isinstance(e, auth.exceptions.ResponseException):
                handle_auth_response_exception(e)
                raise AssertionError
            raise

        self.last_response = resp
        self.last_response_queue.append(resp)

        raise_for_resource_server_response(resp)
        return resp
