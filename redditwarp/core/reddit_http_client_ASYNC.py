
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Mapping, MutableMapping, MutableSequence
    from ..http.session_base_ASYNC import SessionBase
    from .authorizer_ASYNC import Authorizer, Authorized
    from ..http.request import Request
    from ..http.response import Response

import sys
from collections import deque

from .. import __about__
from .. import auth
from .. import http
from ..auth.exceptions import raise_for_resource_server_response
from ..auth.const import RESOURCE_BASE_URL
from ..http.http_client_ASYNC import HTTPClient
from ..http.transport.ASYNC import transport_info_registry
from .exceptions import handle_auth_response_exception

class RedditHTTPClient(HTTPClient):
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
        self.authorized_requestor: Optional[Authorized] = None
        self.user_agent = self.user_agent_start = get_user_agent(session)
        self.timeout = 8
        self.base_url = RESOURCE_BASE_URL

        self.last_request: Optional[Request] = None
        self.last_request_queue: MutableSequence[Request] = deque(maxlen=16)
        self.last_response: Optional[Response] = None
        self.last_response_queue: MutableSequence[Response] = deque(maxlen=16)
        self.last_transfer: Optional[tuple[Request, Response]] = None
        self.last_transfer_queue: MutableSequence[tuple[Request, Response]] = deque(maxlen=16)
        self.last_transmit: Optional[tuple[Request, Optional[Response]]] = None
        self.last_transmit_queue: MutableSequence[tuple[Request, Optional[Response]]] = deque(maxlen=16)

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        resp = None
        try:
            resp = await super().send(request, timeout=timeout)
        except (
            http.exceptions.ResponseException,
            auth.exceptions.ResponseException,
        ) as e:
            resp = e.response

            if isinstance(e, auth.exceptions.ResponseException):
                raise handle_auth_response_exception(e)

            raise

        finally:
            self.last_request = request
            self.last_response = None
            self.last_transfer = None
            self.last_transmit = (request, resp)
            self.last_request_queue.append(request)
            self.last_transmit_queue.append(self.last_transmit)
            if resp is not None:
                self.last_response = resp
                self.last_transfer = (request, resp)
                self.last_response_queue.append(resp)
                self.last_transfer_queue.append(self.last_transfer)

        raise_for_resource_server_response(resp)
        return resp


def get_user_agent(session: object) -> str:
    transport_token = ''
    ti = transport_info_registry.get(session.__module__)
    if ti is not None:
        transport_token = f" {ti.name}/{ti.version}"

    py_version = '.'.join(map(str, sys.version_info[:2]))
    return (
        f"{__about__.__title__}/{__about__.__version__}"
        f" Python/{py_version}"
        f"{transport_token}"
    )
