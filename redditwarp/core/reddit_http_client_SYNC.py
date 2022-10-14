
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableMapping
if TYPE_CHECKING:
    from ..http.session_base_SYNC import SessionBase
    from ..http.requestor_SYNC import Requestor

from ..auth.const import RESOURCE_BASE_URL, TOKEN_OBTAINMENT_URL
from ..http.http_client_SYNC import BasicRequestDefaultsHTTPClient
from ..auth.typedefs import AuthorizationGrantType as AuthorizationGrant
from .authorizer_SYNC import Authorized
from .rate_limited_SYNC import RateLimited
from .recorded_SYNC import Recorded
from .reddit_give_me_json_please_SYNC import RedditGiveMeJSONPlease
from .reddit_token_obtainment_client_SYNC import RedditTokenObtainmentClient
from ..http.transport.SYNC import new_session
from ..http.util.case_insensitive_dict import CaseInsensitiveDict
from .user_agent_SYNC import get_user_agent_from_session
from ..auth.token import Token
from .recorded_SYNC import Last
from .authorizer_SYNC import Authorizer


class RedditHTTPClient(BasicRequestDefaultsHTTPClient):
    """An HTTP client specialised for this library."""

    @property
    def user_agent(self) -> str:
        return self.headers.get('User-Agent', '')

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        self.headers['User-Agent'] = value

    @user_agent.deleter
    def user_agent(self) -> None:
        self.headers.pop('User-Agent', None)

    @property
    def last(self) -> Last:
        return self.get_last()

    def __init__(self,
        session: SessionBase,
        requestor: Optional[Requestor] = None,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        last: Optional[Last] = None,
    ) -> None:
        super().__init__(session, requestor, params=params, headers=headers)
        self.base_url: str = RESOURCE_BASE_URL
        self.user_agent_lead: str = ''
        self._last: Optional[Last] = last

    def get_last(self) -> Last:
        if self._last is None:
            raise RuntimeError('value not set')
        return self._last

    def set_last(self, value: Last) -> None:
        self._last = value


class PublicAPIRedditHTTPClient(RedditHTTPClient):
    """An HTTP client for making requests to the public Reddit REST API."""

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


def build_public_api_reddit_http_client(
    client_id: str,
    client_secret: str,
    grant: AuthorizationGrant,
    *,
    session: Optional[SessionBase] = None,
) -> PublicAPIRedditHTTPClient:
    if session is None:
        session = new_session()
    ua = get_user_agent_from_session(session)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    recorder = Recorded(session)
    last = Last(recorder)
    token_client = RedditTokenObtainmentClient(
        session,
        TOKEN_OBTAINMENT_URL,
        (client_id, client_secret),
        grant,
        headers=headers,
    )
    authorizer = Authorizer(token_client)
    requestor = RedditGiveMeJSONPlease(RateLimited(Authorized(recorder, authorizer)))
    http = PublicAPIRedditHTTPClient(session, requestor, headers=headers, authorizer=authorizer, last=last)
    http.user_agent_lead = ua
    return http

def build_public_api_reddit_http_client_from_access_token(
    access_token: str,
    *,
    session: Optional[SessionBase] = None,
) -> PublicAPIRedditHTTPClient:
    if session is None:
        session = new_session()
    ua = get_user_agent_from_session(session)
    headers = CaseInsensitiveDict({'User-Agent': ua})
    recorder = Recorded(session)
    last = Last(recorder)
    authorizer = Authorizer(token=Token(access_token))
    requestor = RedditGiveMeJSONPlease(RateLimited(Authorized(recorder, authorizer)))
    http = PublicAPIRedditHTTPClient(session, requestor, headers=headers, authorizer=authorizer, last=last)
    return http
