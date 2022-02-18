
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Optional, Mapping, Union, Callable, Sequence, overload
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.typedefs import AuthorizationGrant
    from .http.payload import RequestFiles

from .http.transport.ASYNC import new_session
from .auth import Token
from .auth import grants
from .core.reddit_token_obtainment_client_ASYNC import RedditTokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL
from .core.reddit_http_client_ASYNC import RedditHTTPClient, get_user_agent
from .core.authorizer_ASYNC import Authorizer, Authorized
from .core.rate_limited_ASYNC import RateLimited
from .core.recorded_ASYNC import Recorded, Last
from .util.praw_config import get_praw_config
from .exceptions import raise_for_reddit_error, raise_for_non_json_response
from .http.util.json_load import json_loads_response
from .util.redditwarp_installed_client_credentials import get_redditwarp_client_id, get_installed_client_grant
from .reddit_internal_api.auth.reddit_internal_api_token_obtainment_client_ASYNC import new_reddit_internal_api_token_obtainment_client
from .reddit_internal_api.core.dark_reddit_http_client_ASYNC import DarkRedditHTTPClient
from .reddit_internal_api.core.authorizer_ASYNC import Authorizer as DarkAuthorizer, Authorized as DarkAuthorized
from .reddit_internal_api.core.rate_limited_ASYNC import RateLimited as DarkRateLimited
from .http.misc.apply_params_and_headers_ASYNC import ApplyDefaultHeaders
from .http.util.case_insensitive_dict import CaseInsensitiveDict


class Client:
    _TSelf = TypeVar('_TSelf', bound='Client')

    @classmethod
    def from_http(cls: type[_TSelf], http: RedditHTTPClient, dark_http: Optional[DarkRedditHTTPClient] = None) -> _TSelf:
        self = cls.__new__(cls)

        if dark_http is None:
            session = http.session
            headers = http.headers
            recorder = Recorded(session)
            last = Last(recorder)
            token_client = new_reddit_internal_api_token_obtainment_client(ApplyDefaultHeaders(session, headers))
            authorizer = DarkAuthorizer(token_client)
            requestor = DarkRateLimited(DarkAuthorized(recorder, authorizer))
            dark_http = DarkRedditHTTPClient(session, requestor, headers=headers, authorizer=authorizer, last=last)

        self._init(http, dark_http)
        return self

    @classmethod
    def from_access_token(cls: type[_TSelf], access_token: str) -> _TSelf:
        session = new_session()
        headers = CaseInsensitiveDict({'User-Agent': get_user_agent(session)})
        recorder = Recorded(session)
        last = Last(recorder)
        authorizer = Authorizer(token=Token(access_token))
        requestor = RateLimited(Authorized(recorder, authorizer))
        http = RedditHTTPClient(session, requestor, headers=headers, authorizer=authorizer, last=last)
        return cls.from_http(http)

    @classmethod
    def from_praw_ini(cls: type[_TSelf], site_name: str) -> _TSelf:
        config = get_praw_config()
        section_name = site_name or config.default_section
        try:
            section = config[section_name]
        except KeyError:
            empty = not any(s.values() for s in config.values())
            msg = f"No section {section_name!r} in{' empty' if empty else ''} praw.ini config"
            class StrReprStr(str):
                def __repr__(self) -> str:
                    return str(self)
            raise KeyError(StrReprStr(msg)) from None

        get = section.get
        grant_creds: Sequence[str] = ()
        if (refresh_token := get('refresh_token')) is not None:
            grant_creds = (refresh_token,)
        elif (username := get('username')) is not None and (password := get('password')) is not None:
            grant_creds = (username, password)

        self = cls(
            get('client_id'),
            get('client_secret'),
            *grant_creds,
        )
        if x := get('user_agent'):
            self.set_user_agent(x)
        return self

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, client_id: str, client_secret: str, /) -> None: ...
    @overload
    def __init__(self, client_id: str, client_secret: str, /, *, grant: Mapping[str, str]) -> None: ...
    @overload
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, /) -> None: ...
    @overload
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, /) -> None: ...
    def __init__(self, *creds: str, grant: Optional[AuthorizationGrant] = None) -> None:
        client_id = client_secret = ''
        n = len(creds)
        if n == 0:
            client_id = get_redditwarp_client_id()
            grant = get_installed_client_grant()
        elif n == 2:
            client_id, client_secret = creds
            if grant is None:
                grant = grants.ClientCredentialsGrant()
        elif n == 3:
            client_id, client_secret, refresh_token = creds
            grant = grants.RefreshTokenGrant(refresh_token)
        elif n == 4:
            client_id, client_secret, username, password = creds
            grant = grants.ResourceOwnerPasswordCredentialsGrant(username, password)
        else:
            raise TypeError

        session = new_session()
        headers = CaseInsensitiveDict({'User-Agent': get_user_agent(session)})

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
        requestor = RateLimited(Authorized(recorder, authorizer))
        http = RedditHTTPClient(session, requestor, headers=headers, authorizer=authorizer, last=last)

        recorder = Recorded(session)
        last = Last(recorder)
        dark_token_client = new_reddit_internal_api_token_obtainment_client(
            ApplyDefaultHeaders(session, headers),
        )
        dark_authorizer = DarkAuthorizer(dark_token_client)
        dark_requestor = DarkRateLimited(DarkAuthorized(recorder, dark_authorizer))
        dark_http = DarkRedditHTTPClient(session, dark_requestor, headers=headers, authorizer=dark_authorizer, last=last)

        self._init(http, dark_http)

    def _init(self, http: RedditHTTPClient, dark_http: DarkRedditHTTPClient) -> None:
        self.http: RedditHTTPClient = http
        self.dark_http: DarkRedditHTTPClient = dark_http
        self.last_value: Any = None

        # Delay heavy import till client instantiation
        # instead of library import.
        from .siteprocs.ASYNC import SiteProcedures
        self.p: SiteProcedures = SiteProcedures(self)
        from .reddit_internal_api.siteprocs.ASYNC import SiteProcedures as DarkSiteProcedures
        self.q: DarkSiteProcedures = DarkSiteProcedures(self)

    async def __aenter__(self: _TSelf) -> _TSelf:
        return self

    async def __aexit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def close(self) -> None:
        await self.http.close()

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
        snub: Optional[Callable[[Any], None]] = raise_for_reddit_error,
    ) -> Any:
        json_data = None
        try:
            resp = await self.http.request(verb, uri, params=params, headers=headers,
                    data=data, json=json, files=files, timeout=timeout)

            if resp.data:
                try:
                    json_data = json_loads_response(resp)
                except ValueError as cause:
                    try:
                        raise_for_non_json_response(resp)
                    except Exception as exc:
                        raise exc from cause
                    raise

                if snub is not None:
                    snub(json_data)
        finally:
            self.last_value = json_data

        resp.raise_for_status()
        return json_data

    async def dark_request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
    ) -> Any:
        resp = await self.dark_http.request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files, timeout=timeout)
        resp.raise_for_status()
        return json_loads_response(resp)

    def set_access_token(self, access_token: str) -> None:
        self.http.authorizer.token = Token(access_token)

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_lead
        if s is not None:
            ua = f'{ua} Bot !-- {s}'
        self.http.user_agent = ua

RedditClient: type[Client] = Client
Reddit: type[Client] = Client
