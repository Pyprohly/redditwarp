
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableMapping
if TYPE_CHECKING:
    from ..http.handler_SYNC import Handler

from .const import RESOURCE_BASE_URL, TOKEN_OBTAINMENT_URL
from ..http.http_client_SYNC import HTTPClient
from ..auth.types import AuthorizationGrant
from .authorizer_SYNC import Authorized
from .rate_limited_SYNC import RateLimited
from .recorded_SYNC import Recorded
from .reddit_please_send_json_SYNC import RedditPleaseSendJSON
from .reddit_token_obtainment_client_SYNC import RedditTokenObtainmentClient
from ..http.transport.reg_SYNC import new_connector
from ..http.util.case_insensitive_dict import CaseInsensitiveDict
from ..http.misc.apply_params_and_headers_SYNC import ApplyDefaultHeaders
from .user_agent_SYNC import get_user_agent
from ..auth.token import Token
from .recorded_SYNC import Last
from .authorizer_SYNC import Authorizer
from ..http.send_params import SendParams
from ..http.exchange import Exchange
from .direct_by_origin_SYNC import DirectByOrigin


DEFAULT_TIMEOUT: float = 8


class RedditHTTPClient(HTTPClient):
    """An HTTP client specialised for the purposes of this library."""

    @property
    def last(self) -> Last:
        return self._last

    def __init__(self, handler: Handler, *,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        recorder = Recorded(handler)
        super().__init__(recorder)
        self.base_url: str = RESOURCE_BASE_URL
        self.timeout: float = DEFAULT_TIMEOUT
        self.user_agent_base: str = ''
        self.headers: MutableMapping[str, str] = CaseInsensitiveDict() if headers is None else headers
        self._last: Last = Last(recorder)

    def send(self, p: SendParams) -> Exchange:
        (_d := p.requisition.headers).update({**self.headers, **_d})
        return super().send(p)

    def get_user_agent(self) -> str:
        return self.headers.get('User-Agent', '')

    def set_user_agent(self, value: Optional[str]) -> None:
        if value is not None:
            self.headers['User-Agent'] = value


class PublicRedditHTTPClient(RedditHTTPClient):
    """An HTTP client for making requests to the public Reddit REST API."""

    @property
    def authorizer(self) -> Authorizer:
        return self.fetch_authorizer()

    def __init__(self, handler: Handler, *,
        headers: Optional[MutableMapping[str, str]] = None,
        authorizer: Optional[Authorizer] = None,
    ) -> None:
        super().__init__(handler, headers=headers)
        self._authorizer: Optional[Authorizer] = authorizer

    def fetch_authorizer(self) -> Authorizer:
        if self._authorizer is None:
            raise RuntimeError('value not set')
        return self._authorizer

    def fast_set_authorizer(self, value: Optional[Authorizer]) -> None:
        """Changes the value of `self.authorizer`.

        Note, this attribute is just a holder and changing its value will not
        change the underlying authorizer.
        """
        self._authorizer = value


def build_public_reddit_http_client(
    client_id: str,
    client_secret: str,
    grant: AuthorizationGrant,
) -> PublicRedditHTTPClient:
    connector = new_connector()
    ua = get_user_agent(module_member=connector)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    token_client = RedditTokenObtainmentClient(
        HTTPClient(ApplyDefaultHeaders(connector, headers)),
        TOKEN_OBTAINMENT_URL,
        (client_id, client_secret),
        grant,
    )
    authorizer = Authorizer(token_client)
    handler: Handler
    handler = RedditPleaseSendJSON(RateLimited(Authorized(connector, authorizer)))
    handler = DirectByOrigin(connector, {RESOURCE_BASE_URL: handler})
    http = PublicRedditHTTPClient(handler, headers=headers, authorizer=authorizer)
    http.user_agent_base = ua
    return http

def build_public_reddit_http_client_from_access_token(
    access_token: str,
) -> PublicRedditHTTPClient:
    connector = new_connector()
    ua = get_user_agent(module_member=connector)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    authorizer = Authorizer(token=Token(access_token))
    handler: Handler
    handler = RedditPleaseSendJSON(RateLimited(Authorized(connector, authorizer)))
    handler = DirectByOrigin(connector, {RESOURCE_BASE_URL: handler})
    http = PublicRedditHTTPClient(handler, headers=headers, authorizer=authorizer)
    http.user_agent_base = ua
    return http
