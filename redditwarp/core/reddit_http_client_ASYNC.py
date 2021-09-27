
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Mapping, MutableMapping
    from ..http.session_base_ASYNC import SessionBase
    from .authorizer_ASYNC import Authorizer
    from ..http.response import Response
    from ..http.requestor_ASYNC import Requestor

import platform

from .. import __about__
from ..auth.const import RESOURCE_BASE_URL
from ..http.http_client_ASYNC import HTTPClient
from ..http.transport.ASYNC import transport_info_registry
from .record_messages_requestor_ASYNC import RecordLastMessages

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
    def authorizer(self) -> Authorizer:
        return self.get_authorizer()

    @property
    def last(self) -> RecordLastMessages.State:
        return self.recorder.last

    @property
    def last_response(self) -> Optional[Response]:
        return self.recorder.last.response

    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
        authorizer: Optional[Authorizer] = None,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        params = dict(self.DEFAULT_PARAMS) if params is None else params
        self.recorder = RecordLastMessages(session if requestor is None else requestor)
        super().__init__(session, self.recorder, params=params, headers=headers)
        self._authorizer = authorizer
        self.user_agent = self.user_agent_start = get_user_agent(session)
        self.base_url = RESOURCE_BASE_URL

    def get_authorizer(self) -> Authorizer:
        if self._authorizer is None:
            raise RuntimeError('value not set')
        return self._authorizer

    def set_authorizer(self, value: Authorizer) -> None:
        self._authorizer = value

def get_user_agent(session: object) -> str:
    tokens = [
        f"{__about__.__title__}/{__about__.__version__}",
        f"Python/{platform.python_version()}",
    ]

    if session:
        ti = transport_info_registry.get(session.__module__)
        if ti:
            tokens.append(f"{ti.name}/{ti.version}")

    return ' '.join(tokens)
