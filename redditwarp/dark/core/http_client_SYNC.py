
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableMapping
if TYPE_CHECKING:
    from ...http.handler_SYNC import Handler

from ...core.http_client_SYNC import HTTPClient
from ...core.reddit_please_send_json_SYNC import RedditPleaseSendJSON
from ...http.misc_handlers.apply_params_and_headers_SYNC import ApplyDefaultHeaders
from ...http.transport.auto_SYNC import new_connector
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ..auth.token_obtainment_client_SYNC import new_token_obtainment_client
from .authorizer_SYNC import Authorizer, Authorized
from .rate_limited_SYNC import RateLimited
from ...core.ua_SYNC import get_suitable_user_agent
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
    ua = get_suitable_user_agent(connector.__module__)
    headers = CaseInsensitiveDict({'User-Agent': ua})

    http = BaseHTTPClient(ApplyDefaultHeaders(connector, headers))
    authorizer = Authorizer(new_token_obtainment_client(http))
    hdlr = RedditPleaseSendJSON(RateLimited(Authorized(connector, authorizer)))
    hdlr1 = DirectByOrigin(connector, {x: hdlr for x in TRUSTED_ORIGINS})

    http = RedditHTTPClient(hdlr1, headers=headers, authorizer=authorizer)
    return http
