
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableMapping
if TYPE_CHECKING:
    from .authorizer_ASYNC import Authorizer
    from ...http.handler_ASYNC import Handler

from ...core.http_client_ASYNC import HTTPClient
from ...core.rate_limited_ASYNC import RateLimited
from ...core.reddit_please_send_json_ASYNC import RedditPleaseSendJSON
from ...http.misc.apply_params_and_headers_ASYNC import ApplyDefaultHeaders
from ...http.transport.reg_ASYNC import new_connector
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ..auth.internal_reddit_api_token_obtainment_client_ASYNC import new_internal_reddit_api_token_obtainment_client
from .authorizer_ASYNC import Authorized
from ...core.user_agent_ASYNC import get_user_agent
from ...http.http_client_ASYNC import HTTPClient as BaseHTTPClient


class InternalRedditHTTPClient(HTTPClient):
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
        self._authorizer = value


def build_internal_reddit_http_client() -> InternalRedditHTTPClient:
    connector = new_connector()
    ua = get_user_agent(module_member=connector)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    http = BaseHTTPClient(ApplyDefaultHeaders(connector, headers))
    token_client = new_internal_reddit_api_token_obtainment_client(http)
    authorizer = Authorizer(token_client)
    handler = RedditPleaseSendJSON(RateLimited(Authorized(connector, authorizer)))
    http = InternalRedditHTTPClient(handler, headers=headers, authorizer=authorizer)
    return http
