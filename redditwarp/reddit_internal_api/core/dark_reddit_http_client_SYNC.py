
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, MutableMapping
    from ...http.session_base_SYNC import SessionBase
    from .authorizer_SYNC import Authorizer
    from ...core.recorded_SYNC import Last
    from ...http.requestor_SYNC import Requestor

from ...http.http_client_SYNC import HTTPClient
from ...core.reddit_http_client_SYNC import get_user_agent

class DarkRedditHTTPClient(HTTPClient):
    @property
    def authorizer(self) -> Authorizer:
        return self.get_authorizer()

    @property
    def last(self) -> Last:
        return self.get_last()

    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        authorizer: Optional[Authorizer] = None,
        last: Optional[Last] = None,
    ) -> None:
        super().__init__(session, requestor, params=params, headers=headers)
        self._authorizer = authorizer
        self._last = last
        if (key := 'User-Agent') not in self.headers:
            self.headers[key] = get_user_agent(session)

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
