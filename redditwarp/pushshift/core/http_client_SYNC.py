
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...http.http_client_SYNC import HTTPClient as BaseHTTPClient

from ...core.http_client_SYNC import HTTPClient
from ...http.transport.reg_SYNC import new_connector
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ...core.user_agent_SYNC import get_user_agent
from .const import RESOURCE_BASE_URL
from .rate_limited_SYNC import RateLimited

def build_http_client() -> BaseHTTPClient:
    connector = new_connector()
    ua = get_user_agent(module_member=connector)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    http = HTTPClient(RateLimited(connector), headers=headers)
    http.base_url = RESOURCE_BASE_URL
    return http
