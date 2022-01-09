
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Optional, Mapping, Union, Callable
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.typedefs import ClientCredentials, AuthorizationGrant
    from .http.payload import RequestFiles

from .http.transport._ASYNC_ import new_session
from .auth import Token
from .auth.util import auto_grant_factory
from .core.reddit_token_obtainment_client_ASYNC import RedditTokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL
from .core.reddit_http_client_ASYNC import RedditHTTPClient
from .core.authorizer_ASYNC import Authorizer, Authorized
from .core.rate_limited_ASYNC import RateLimited
from .core.recorded_ASYNC import Recorded, Last
from .util.praw_config import get_praw_config
from .exceptions import raise_for_reddit_error, raise_for_non_json_response
from .http.util.json_load import json_loads_response

class CoreClient:
    _TSelf = TypeVar('_TSelf', bound='CoreClient')

    @classmethod
    def from_creds(cls: type[_TSelf], client_creds: ClientCredentials, grant: AuthorizationGrant) -> _TSelf:
        return cls(*client_creds, grant=grant)

    @classmethod
    def from_http(cls: type[_TSelf], http: RedditHTTPClient) -> _TSelf:
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_access_token(cls: type[_TSelf], access_token: str) -> _TSelf:
        session = new_session()
        recorder = Recorded(session)
        last = Last(recorder)
        authorizer = Authorizer(token=Token(access_token))
        requestor = RateLimited(Authorized(recorder, authorizer))
        http = RedditHTTPClient(session, requestor, authorizer=authorizer, last=last)
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
        self = cls(
            client_id=get('client_id'),
            client_secret=get('client_secret'),
            refresh_token=get('refresh_token'),
            username=get('username'),
            password=get('password'),
        )
        if x := get('user_agent'):
            self.set_user_agent(x)
        return self

    def __init__(self,
            client_id: str, client_secret: str,
            refresh_token: Optional[str] = None,
            *,
            username: Optional[str] = None, password: Optional[str] = None,
            grant: Optional[AuthorizationGrant] = None):
        grant_creds = (refresh_token, username, password)
        if grant is None:
            grant = auto_grant_factory(*grant_creds)
        elif any(grant_creds):
            raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

        session = new_session()
        recorder = Recorded(session)
        last = Last(recorder)
        token_client = RedditTokenObtainmentClient(
            session,
            TOKEN_OBTAINMENT_URL,
            (client_id, client_secret),
            grant,
        )
        authorizer = Authorizer(token_client)
        requestor = RateLimited(Authorized(recorder, authorizer))
        http = RedditHTTPClient(session, requestor, authorizer=authorizer, last=last)
        token_client.headers = http.headers
        self._init(http)

    def _init(self, http: RedditHTTPClient) -> None:
        self.http: RedditHTTPClient = http
        self.last_value: Any = None

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

    def set_access_token(self, access_token: str) -> None:
        self.http.authorizer.token = Token(access_token)

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_lead
        if s is not None:
            ua = f'{ua} Bot !-- {s}'
        self.http.user_agent = ua

class Client(CoreClient):
    def _init(self, http: RedditHTTPClient) -> None:
        super()._init(http)
        from .siteprocs._ASYNC_ import SiteProcedures
        self.p: SiteProcedures = SiteProcedures(self)
