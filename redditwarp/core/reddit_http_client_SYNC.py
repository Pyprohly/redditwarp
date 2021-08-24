
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Mapping, MutableMapping
    from ..http.session_base_SYNC import SessionBase
    from .authorizer_SYNC import Authorizer, Authorized
    from ..http.request import Request
    from ..http.response import Response
    from ..http.requestor_SYNC import Requestor

import sys

from .. import __about__
from .. import auth
from ..auth.exceptions import raise_for_resource_server_response
from ..auth.const import RESOURCE_BASE_URL
from ..http.http_client_SYNC import HTTPClient
from ..http.transport.SYNC import transport_info_registry
from .exceptions import handle_auth_response_exception
from .record_messages_requestor_SYNC import RecordLastMessages

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
            raise RuntimeError('.authorized_requestor missing')
        self.authorized_requestor.authorizer = value

    @property
    def last(self) -> RecordLastMessages.State:
        return self.recorder.last

    @property
    def last_response(self) -> Optional[Response]:
        return self.recorder.last.response

    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        authorized_requestor: Optional[Authorized] = None,
    ) -> None:
        params = dict(self.DEFAULT_PARAMS) if params is None else params
        self.recorder = RecordLastMessages(session if requestor is None else requestor)
        super().__init__(session, self.recorder, params=params, headers=headers)
        self.authorized_requestor: Optional[Authorized] = authorized_requestor
        self.user_agent = self.user_agent_start = get_user_agent(session)
        self.timeout = 8
        self.base_url = RESOURCE_BASE_URL

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        try:
            resp = super().send(request, timeout=timeout)
        except auth.exceptions.ResponseException as e:
            raise handle_auth_response_exception(e)

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
