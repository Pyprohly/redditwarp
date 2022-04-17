
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...http.session_base_SYNC import SessionBase

from ...core.reddit_http_client_SYNC import RedditHTTPClient
from ...core.rate_limited_SYNC import RateLimited
from ...core.recorded_SYNC import Recorded
from ...core.reddit_give_me_json_please_SYNC import RedditGiveMeJSONPlease
from ...http.transport.SYNC import new_session
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ...util.user_agent_SYNC import get_user_agent_from_session
from ...http.http_client_SYNC import HTTPClient
from ..const import PUSHSHIFT_BASE_URL
from ...core.recorded_SYNC import Last

def build_http_client(
    *,
    session: Optional[SessionBase] = None,
) -> HTTPClient:
    if session is None:
        session = new_session()
    ua = get_user_agent_from_session(session)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    recorder = Recorded(session)
    last = Last(recorder)
    requestor = RedditGiveMeJSONPlease(RateLimited(recorder))
    http = RedditHTTPClient(session, requestor, headers=headers, last=last)
    http.base_url = PUSHSHIFT_BASE_URL
    return http
