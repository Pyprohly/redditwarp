
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Optional, Mapping, Union, Callable, Sequence, overload
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.types import AuthorizationGrant
    from .http.payload import RequestFiles
    from .core.reddit_http_client_ASYNC import RedditHTTPClient

from configparser import ConfigParser

from .auth import Token
from .auth import grants
from .core.auth import grants as core_grants
from .core.reddit_http_client_ASYNC import (
    PublicRedditHTTPClient,
    build_public_reddit_http_client,
    build_public_reddit_http_client_from_access_token,
)
from .util.praw_config import get_praw_ini_potential_file_locations
from .exceptions import raise_for_reddit_error, raise_for_non_json_response
from .http.util.json_load import json_loads_response
from .util.redditwarp_installed_client_credentials import get_redditwarp_client_id, get_device_id


class Client:
    _TSelf = TypeVar('_TSelf', bound='Client')

    @classmethod
    def from_http(cls: type[_TSelf], http: RedditHTTPClient) -> _TSelf:
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_access_token(cls: type[_TSelf], access_token: str) -> _TSelf:
        http = build_public_reddit_http_client_from_access_token(access_token)
        return cls.from_http(http)

    @classmethod
    def from_praw_config(cls: type[_TSelf], section_name: str, *, filename: Optional[str] = None) -> _TSelf:
        config = ConfigParser()
        config.read(get_praw_ini_potential_file_locations() if filename is None else filename)
        section_name = section_name or config.default_section
        try:
            section = config[section_name]
        except KeyError:
            empty = not any(s.values() for s in config.values())
            msg = f"No section named {section_name!r} in{' empty' if empty else ''} praw.ini config."
            class StrReprStr(str):
                def __repr__(self) -> str:
                    return str(self)
            raise KeyError(StrReprStr(msg)) from None

        get = section.get
        grant_creds: Sequence[str] = ()
        if refresh_token := get('refresh_token'):
            grant_creds = (refresh_token,)
        elif (username := get('username')) and (password := get('password')):
            grant_creds = (username, password)
        self = cls(
            section['client_id'],
            section['client_secret'],
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
    def __init__(self, client_id: str, client_secret: str, /, *, grant: AuthorizationGrant) -> None: ...
    @overload
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, /) -> None: ...
    @overload
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, /) -> None: ...
    def __init__(self, *creds: str, grant: Optional[AuthorizationGrant] = None) -> None:
        client_id = client_secret = ''
        n = len(creds)
        if n == 0:
            client_id = get_redditwarp_client_id()
            grant = core_grants.InstalledClientGrant(get_device_id())
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

        http = build_public_reddit_http_client(client_id, client_secret, grant)
        self._init(http)

    def _init(self, http: RedditHTTPClient) -> None:
        self.http: RedditHTTPClient = http
        self.last_value: Any = None

        # Delay heavy import till client instantiation
        # instead of library import.
        from .siteprocs.ASYNC import SiteProcedures
        self.p: SiteProcedures = SiteProcedures(self)

    async def __aenter__(self: _TSelf) -> _TSelf:
        return self

    async def __aexit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def close(self) -> None:
        await self.http.close()

    async def request(self,
        verb: str,
        url: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
        snub: Optional[Callable[[Any], None]] = raise_for_reddit_error,
    ) -> Any:
        json_data = None
        try:
            resp = await self.http.request(verb, url, params=params, headers=headers,
                    data=data, json=json, files=files, timeout=timeout, follow_redirects=follow_redirects)

            if resp.data:
                try:
                    json_data = json_loads_response(resp)
                except ValueError:
                    try:
                        raise_for_non_json_response(resp)
                    except Exception as exc:
                        raise exc from None
                    raise

                if snub is not None:
                    snub(json_data)
        finally:
            self.last_value = json_data

        resp.raise_for_status()
        return json_data

    def set_access_token(self, access_token: str) -> None:
        http = self.http
        if not isinstance(http, PublicRedditHTTPClient):
            raise RuntimeError(f'self.http must be {PublicRedditHTTPClient.__name__}')
        http.authorizer.set_token(Token(access_token))

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_base
        if s is not None:
            ua = f"{ua} Bot !-- {s}"
        self.http.set_user_agent(ua)

RedditClient: type[Client] = Client
Reddit: type[Client] = Client
RedditWarp: type[Client] = Client
