
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableMapping
if TYPE_CHECKING:
    from ...http.session_base_SYNC import SessionBase
    from .authorizer_SYNC import Authorizer
    from ...core.recorded_SYNC import Last
    from ...http.requestor_SYNC import Requestor

from ...core.reddit_http_client_SYNC import RedditHTTPClient
from ...core.rate_limited_SYNC import RateLimited
from ...core.recorded_SYNC import Recorded
from ...core.reddit_give_me_json_please_SYNC import RedditGiveMeJSONPlease
from ...http.misc.apply_params_and_headers_SYNC import ApplyDefaultHeaders
from ...http.transport.reg_SYNC import new_session
from ...http.util.case_insensitive_dict import CaseInsensitiveDict
from ..auth.reddit_internal_api_token_obtainment_client_SYNC import new_reddit_internal_api_token_obtainment_client
from .authorizer_SYNC import Authorized
from ...core.user_agent_SYNC import get_user_agent_from_session


class InternalAPIRedditHTTPClient(RedditHTTPClient):
    @property
    def authorizer(self) -> Authorizer:
        return self.get_authorizer()

    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        last: Optional[Last] = None,
        authorizer: Optional[Authorizer] = None,
    ) -> None:
        super().__init__(session, requestor, params=params, headers=headers, last=last)
        self._authorizer: Optional[Authorizer] = authorizer

    def get_authorizer(self) -> Authorizer:
        if self._authorizer is None:
            raise RuntimeError('value not set')
        return self._authorizer

    def set_authorizer(self, value: Authorizer) -> None:
        self._authorizer = value


def build_internal_api_reddit_http_client(
    *,
    session: Optional[SessionBase] = None,
) -> InternalAPIRedditHTTPClient:
    if session is None:
        session = new_session()
    ua = get_user_agent_from_session(session)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    recorder = Recorded(session)
    last = Last(recorder)
    token_client = new_reddit_internal_api_token_obtainment_client(ApplyDefaultHeaders(session, headers))
    authorizer = Authorizer(token_client)
    requestor = RedditGiveMeJSONPlease(RateLimited(Authorized(recorder, authorizer)))
    http = InternalAPIRedditHTTPClient(session, requestor, headers=headers, authorizer=authorizer, last=last)
    return http
