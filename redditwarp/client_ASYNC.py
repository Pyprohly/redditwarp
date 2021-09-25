
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Type, Optional, Mapping, Union
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.typedefs import ClientCredentials, AuthorizationGrant
    from .http.payload import RequestFiles

from .http.util.json_load import json_loads_response
from .http.transport.ASYNC import new_session
from .auth import Token
from .auth.util import auto_grant_factory
from .auth.reddit_token_obtainment_client_ASYNC import RedditTokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL
from .core.reddit_http_client_ASYNC import RedditHTTPClient
from .core.authorizer_ASYNC import Authorizer, Authorized
from .core.rate_limited_ASYNC import RateLimited
from .util.praw_config import get_praw_config
from .util.except_without_context import except_without_context
from .exceptions import (
    raise_for_status,
    handle_non_json_response,
    raise_for_json_object_data,
)

'''
from .util.imports import lazy_import
if TYPE_CHECKING:
    from .siteprocs import ASYNC as siteprocs
else:
    siteprocs = lazy_import('.siteprocs.ASYNC', __package__)
'''

class CoreClient:
    _USER_AGENT_CUSTOM_DESCRIPTION_SEPARATOR = ' Bot !-- '
    _TSelf = TypeVar('_TSelf', bound='CoreClient')

    @classmethod
    def from_creds(cls: Type[_TSelf], client_creds: ClientCredentials, grant: AuthorizationGrant) -> _TSelf:
        return cls(*client_creds, grant=grant)

    @classmethod
    def from_http(cls: Type[_TSelf], http: RedditHTTPClient) -> _TSelf:
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_access_token(cls: Type[_TSelf], access_token: str) -> _TSelf:
        session = new_session()
        authorizer = Authorizer(token=Token(access_token))
        requestor = RateLimited(Authorized(session, authorizer))
        http = RedditHTTPClient(session, requestor, authorizer)
        return cls.from_http(http)

    @classmethod
    def from_praw_ini(cls: Type[_TSelf], site_name: str) -> _TSelf:
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
            access_token: Optional[str] = None,
            *,
            username: Optional[str] = None, password: Optional[str] = None,
            grant: Optional[AuthorizationGrant] = None):
        grant_creds = (refresh_token, username, password)
        if grant is None:
            grant = auto_grant_factory(*grant_creds)
        elif any(grant_creds):
            raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

        session = new_session()
        token_client = RedditTokenObtainmentClient(
            session,
            TOKEN_OBTAINMENT_URL,
            (client_id, client_secret),
            grant,
        )
        authorizer = Authorizer(
            token_client,
            (None if access_token is None else Token(access_token)),
        )
        requestor = RateLimited(Authorized(session, authorizer))
        http = RedditHTTPClient(session, requestor, authorizer)
        token_client.headers = http.headers
        self._init(http)

    def _init(self, http: RedditHTTPClient) -> None:
        self.http = http
        self.last_value: Any = None

    async def __aenter__(self: _TSelf) -> _TSelf:
        return self

    async def __aexit__(self,
        exc_type: Optional[Type[BaseException]],
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
    ) -> Any:
        self.last_value = None

        resp = await self.http.request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files, timeout=timeout)

        json_data = None
        if resp.data:
            with except_without_context(ValueError) as xcpt:
                json_data = json_loads_response(resp)
            if xcpt:
                raise handle_non_json_response(resp)

            self.last_value = json_data

            if isinstance(json_data, Mapping):
                raise_for_json_object_data(resp, json_data)

        raise_for_status(resp)
        return json_data

    def set_access_token(self, access_token: str) -> None:
        self.http.authorizer.token = Token(access_token)

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_start
        if s is not None:
            ua += self._USER_AGENT_CUSTOM_DESCRIPTION_SEPARATOR + s
        self.http.user_agent = ua

class Client(CoreClient):
    def _init(self, http: RedditHTTPClient) -> None:
        super()._init(http)
        self.p = ...#siteprocs.ClientProcedures(self)
