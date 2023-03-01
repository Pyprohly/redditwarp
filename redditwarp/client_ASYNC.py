
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Optional, Mapping, Union, Callable, overload
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.types import AuthorizationGrant
    from .http.types import RequestFiles
    from .http.payload import Payload
    from .core.http_client_ASYNC import HTTPClient
    from .types import JSON_ro

from .auth import Token
from .auth import grants
from .core import grants as core_grants
from .core.http_client_ASYNC import (
    RedditHTTPClient,
    build_reddit_http_client,
    build_reddit_http_client_from_access_token,
)
from .exceptions import raise_for_reddit_error, raise_for_non_json_response
from .http.util.json_loading import load_json_from_response
from .util.redditwarp_installed_client_credentials import get_redditwarp_client_id, get_device_id


class Client:
    _TSelf = TypeVar('_TSelf', bound='Client')

    @staticmethod
    def from_praw_config(section_name: str, *, filepath: Optional[str] = None) -> Client:
        from .util.praw_config_ASYNC import client_from_praw_config  # Avoid cyclic import
        return client_from_praw_config(section_name, filepath=filepath)

    @classmethod
    def from_http(cls: type[_TSelf], http: HTTPClient) -> _TSelf:
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_access_token(cls: type[_TSelf], access_token: str) -> _TSelf:
        http = build_reddit_http_client_from_access_token(access_token)
        return cls.from_http(http)

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

        http = build_reddit_http_client(client_id, client_secret, grant)
        self._init(http)

    def _init(self, http: HTTPClient) -> None:
        self.http: HTTPClient = http
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
        json: JSON_ro = None,
        files: Optional[RequestFiles] = None,
        payload: Optional[Payload] = None,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
        snub: Optional[Callable[[JSON_ro], None]] = raise_for_reddit_error,
    ) -> Any:
        json_data = None
        try:
            resp = await self.http.request(verb, url, params=params, headers=headers,
                    data=data, json=json, files=files, payload=payload,
                    timeout=timeout, follow_redirects=follow_redirects)

            if resp.data:
                try:
                    json_data = load_json_from_response(resp)
                except ValueError as cause:
                    try:
                        raise_for_non_json_response(resp)
                    except Exception as exc:
                        raise exc from cause
                    raise

                if snub is not None:
                    snub(json_data)

            resp.ensure_successful_status()
        finally:
            self.last_value = json_data
        return json_data

    def set_access_token(self, access_token: str) -> None:
        http = self.http
        if not isinstance(http, RedditHTTPClient):
            raise RuntimeError(f"self.http must be {RedditHTTPClient.__name__}")
        http.authorizer.set_token(Token(access_token))

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_base
        if s is not None:
            ua = f"{ua} Bot !-- {s}"
        self.http.set_user_agent(ua)

RedditClient = Client
Reddit = Client
RedditWarp = Client
