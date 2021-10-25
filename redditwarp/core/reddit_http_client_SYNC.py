
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Mapping, MutableMapping
    from ..http.session_base_SYNC import SessionBase
    from .authorizer_SYNC import Authorizer
    from .recorded_SYNC import Last
    from ..http.response import Response
    from ..http.requestor_SYNC import Requestor

import sys

from .. import __about__
from ..auth.const import RESOURCE_BASE_URL
from ..http.http_client_SYNC import HTTPClient
from ..http.transport.SYNC import transport_info_registry

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
    def last(self) -> Last:
        return self.get_last()

    @property
    def last_response(self) -> Optional[Response]:
        return self.last.response

    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        authorizer: Optional[Authorizer] = None,
        last: Optional[Last] = None,
    ) -> None:
        params = dict(self.DEFAULT_PARAMS) if params is None else params
        super().__init__(session, requestor, params=params, headers=headers)
        self._authorizer = authorizer
        self._last = last
        self.user_agent_lead: str = get_user_agent(session)
        self.user_agent = self.user_agent_lead
        self.base_url: str = RESOURCE_BASE_URL

    def get_authorizer(self) -> Authorizer:
        if self._authorizer is None:
            raise RuntimeError('value not set')
        return self._authorizer

    def set_authorizer(self, value: Authorizer) -> None:
        self._authorizer = value

    def get_last(self) -> Last:
        if self._last is None:
            raise RuntimeError('value not set')
        return self._last

    def set_last(self, value: Last) -> None:
        self._last = value


def get_user_agent(session: object) -> str:
    tokens = [
        f"{__about__.__title__}/{__about__.__version__}",
        f"Python/{sys.version.split(None, 1)[0]}",
    ]
    if session:
        ti = transport_info_registry.get(session.__module__)
        if ti:
            tokens.append(f"{ti.name}/{ti.version}")
    return ' '.join(tokens)
