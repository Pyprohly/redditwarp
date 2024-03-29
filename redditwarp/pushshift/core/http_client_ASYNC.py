
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...http.http_client_ASYNC import HTTPClient as BaseHTTPClient
    from ...http.transport.connector_ASYNC import Connector

from ...core.http_client_ASYNC import HTTPClient
from ...http.transport.reg_ASYNC import new_connector
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ...core.user_agent_ASYNC import get_user_agent
from .const import RESOURCE_BASE_URL
from .rate_limited_ASYNC import RateLimited

def build_http_client(
    *,
    connector: Optional[Connector] = None,
) -> BaseHTTPClient:
    if connector is None:
        connector = new_connector()
    ua = get_user_agent(module_member=connector)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    http = HTTPClient(RateLimited(connector), headers=headers)
    http.base_url = RESOURCE_BASE_URL
    return http
