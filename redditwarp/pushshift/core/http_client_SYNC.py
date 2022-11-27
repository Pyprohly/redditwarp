
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...http.http_client_SYNC import HTTPClient

from ...core.reddit_http_client_SYNC import RedditHTTPClient
from ...http.transport.reg_SYNC import new_connector
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ...core.user_agent_SYNC import get_user_agent
from .const import PUSHSHIFT_BASE_URL
from .rate_limited_SYNC import RateLimited

def build_http_client() -> HTTPClient:
    connector = new_connector()
    ua = get_user_agent(module_member=connector)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    http = RedditHTTPClient(RateLimited(connector), headers=headers)
    http.base_url = PUSHSHIFT_BASE_URL
    return http
