
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableMapping
if TYPE_CHECKING:
    from ...http.handler_SYNC import Handler

from ...core.http_client_SYNC import HTTPClient
from ...core.rate_limited_SYNC import RateLimited
from ...core.reddit_please_send_json_SYNC import RedditPleaseSendJSON
from ...http.misc.apply_params_and_headers_SYNC import ApplyDefaultHeaders
from ...http.transport.reg_SYNC import new_connector
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ..auth.token_obtainment_client_SYNC import new_token_obtainment_client
from .authorizer_SYNC import Authorizer, Authorized
from ...core.user_agent_SYNC import get_user_agent
from ...http.http_client_SYNC import HTTPClient as BaseHTTPClient
from ...core.direct_by_origin_SYNC import DirectByOrigin
from .const import TRUSTED_ORIGINS


class RedditHTTPClient(HTTPClient):
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


def build_reddit_http_client() -> RedditHTTPClient:
    connector = new_connector()
    ua = get_user_agent(module_member=connector)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    http = BaseHTTPClient(ApplyDefaultHeaders(connector, headers))
    token_client = new_token_obtainment_client(http)
    authorizer = Authorizer(token_client)
    handler: Handler
    handler = RedditPleaseSendJSON(RateLimited(Authorized(connector, authorizer)))
    directions = {x: handler for x in TRUSTED_ORIGINS}
    handler = DirectByOrigin(connector, directions)
    http = RedditHTTPClient(handler, headers=headers, authorizer=authorizer)
    return http
