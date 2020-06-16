
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Type, Optional, Mapping, MutableMapping, Dict, cast, Union
if TYPE_CHECKING:
    from types import TracebackType
    from .http.payload import Payload
    from .http.response import Response

from . import http
from . import auth
from .core.http_client_async import HTTPClient
from .http.misc import json_loads_response
from .auth import ClientCredentials, Token
from .auth.util import auto_grant_factory
from .util.praw_config import get_praw_config
from .http.transport.aiohttp import new_session
from .auth.token_obtainment_client_async import TokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_ENDPOINT_URL, RESOURCE_BASE_URL
from .core.authorizer_async import Authorizer, Authorized
from .core.ratelimited_async import RateLimited
from .core.default_headers_predisposed_async import DefaultHeadersPredisposed
from .exceptions import (
    AuthError,
    APIError,
    HTTPStatusError,
    get_response_content_error,
    raise_for_json_layout_content_error,
    raise_for_variant1_reddit_api_error,
    raise_for_variant2_reddit_api_error,
)
#from .site_procedures import SiteProcedures

AuthorizationGrant = Union[auth.grants.AuthorizationGrant, Mapping[str, Optional[str]]]

interactive_mode = not hasattr(__import__('__main__'), '__file__')

class ClientCore:

    T = TypeVar('T', bound='ClientCore')

    @classmethod
    def from_http(cls: Type[T], http: HTTPClient) -> T:
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_praw_config(cls: Type[T], site_name: str = '') -> T:
        config = get_praw_config()
        section_name = site_name or config.default_section  # type: ignore[attr-defined]
        try:
            section = config[section_name]
        except KeyError:
            class StrReprStr(str):
                def __repr__(self) -> str:
                    return str(self)
            empty = not any(s.values() for s in config.values())
            msg = f"No section {section_name!r} in{' empty' if empty else ''} config"
            raise KeyError(StrReprStr(msg)) from None

        get = section.get
        self = cls(
            client_id=get('client_id'),
            client_secret=get('client_secret'),
            refresh_token=get('refresh_token'),
            username=get('username'),
            password=get('password'),
        )
        if 'user_agent' in section:
            self.set_user_agent(get('user_agent'))
        return self

    @classmethod
    def from_access_token(cls: Type[T], access_token: str) -> T:
        token = Token(access_token)
        session = new_session()
        authorizer = Authorizer(token, None)
        authorized_requestor = Authorized(session, authorizer)
        requestor = RateLimited(authorized_requestor)
        http = HTTPClient(session, requestor, authorized_requestor=authorized_requestor)
        return cls.from_http(http)

    def __init__(self,
            client_id: str, client_secret: str, refresh_token: Optional[str] = None,
            access_token: Optional[str] = None, *,
            username: Optional[str] = None, password: Optional[str] = None,
            grant: Optional[AuthorizationGrant] = None):
        grant_creds = (refresh_token, username, password)
        if grant is None:
            grant = auto_grant_factory(*grant_creds)
            if grant is None:
                raise ValueError("couldn't automatically create a grant from the provided credentials")
        elif any(grant_creds):
            raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

        token = None if access_token is None else Token(access_token)
        session = new_session()
        authorizer = Authorizer(token, None)
        authorized_requestor = Authorized(session, authorizer)
        requestor = RateLimited(authorized_requestor)
        http = HTTPClient(session, requestor, authorized_requestor=authorized_requestor)
        authorizer.token_client = TokenObtainmentClient(
            DefaultHeadersPredisposed(session, http.default_headers),
            TOKEN_OBTAINMENT_ENDPOINT_URL,
            ClientCredentials(client_id, client_secret),
            grant,
        )
        self._init(http)

    def _init(self, http: HTTPClient) -> None:
        self.http = http
        self.last_response: Optional[Response] = None
        self.resource_base_url = RESOURCE_BASE_URL

    async def __aenter__(self) -> ClientCore:
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

    def set_user_agent(self, s: Optional[str]) -> None:
        s = str(s)
        ua = self.http.USER_AGENT_STRING_HEAD
        if s is not None:
            ua += ' Bot -- ' + s
        self.http.user_agent = ua

    async def request(self,
        verb: str,
        path: str,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[MutableMapping[str, str]] = None,
        timeout: float = 8,
        aux_info: Optional[Mapping] = None,
    ) -> Dict[str, Any]:
        uri = self.resource_base_url + path
        try:
            resp = await self.http.request(verb, uri, params=params, payload=payload,
                    data=data, json=json, headers=headers, timeout=timeout, aux_info=aux_info)

        except auth.exceptions.ResponseException as e:
            self.last_response = e.response
            raise AuthError(response=e.response) from e
        except http.exceptions.ResponseException as e:
            self.last_response = e.response
            raise APIError(response=e.response) from e

        self.last_response = resp

        try:
            data = json_loads_response(resp)
        except ValueError:
            raise get_response_content_error(resp) from None

        raise_for_json_layout_content_error(resp, data)
        raise_for_variant1_reddit_api_error(resp, data)
        raise_for_variant2_reddit_api_error(resp, data)

        try:
            resp.raise_for_status()
        except http.exceptions.StatusCodeException as e:
            raise HTTPStatusError(response=resp) from e

        return data

    def set_access_token(self, access_token: str) -> None:
        if self.http.authorizer is None:
            raise RuntimeError('The HTTP client does not know of an authorizer instance to assign a token to')
        self.http.authorizer.token = Token(access_token)

ClientMeta = type
if interactive_mode:
    class ClientMeta(type):  # type: ignore[no-redef]
        def __call__(cls: type, *args: Any, **kwds: Any) -> Client:
            cls = cast(Type[Client], cls)
            if len(args) == 1:
                return cls.from_praw_config(*args)
            return type.__call__(cls, *args, **kwds)

class Client(ClientCore, metaclass=ClientMeta):  # type: ignore[misc]
    T = TypeVar('T', bound='Client')

    def _init(self, http: HTTPClient) -> None:
        super()._init(http)
        self.api = ...#SiteProcedures(self)
        #self.fetch = self.api.fetch
