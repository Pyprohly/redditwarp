
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Type, Optional, Mapping, \
        Union, MutableSequence
if TYPE_CHECKING:
    from types import TracebackType
    from .http.payload import Payload
    from .http.response import Response

from collections import deque

from . import http
from .http.util.json_loads import json_loads_response
from .http.transport.ASYNC import get_default_transporter_name, new_session_factory
from . import auth
from .auth import ClientCredentials, Token
from .auth.util import auto_grant_factory
from .auth.token_obtainment_client_ASYNC import TokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL, RESOURCE_BASE_URL
from . import core
from .core.http_client_ASYNC import HTTPClient
from .core.authorizer_ASYNC import Authorizer, Authorized
from .core.ratelimited_ASYNC import RateLimited
from .util.praw_config import get_praw_config
from .exceptions import (
    UnidentifiedResponseContentError,
    raise_for_status,
    raise_for_response_content_error,
    raise_for_json_layout_content_error,
    raise_for_variant1_reddit_api_error,
    raise_for_variant2_reddit_api_error,
)
#from .util.module_importing import lazy_import;
#if 0: from .api.site_procedures import ASYNC as site_procedures_ASYNC
#site_procedures_ASYNC = lazy_import('.api.site_procedures.ASYNC', __package__)  # noqa: F811

AuthorizationGrant = Union[auth.grants.AuthorizationGrant, Mapping[str, Optional[str]]]

class ClientCore:
    default_transporter_name = None

    T = TypeVar('T', bound='ClientCore')

    @classmethod
    def get_default_transporter_name(cls: Type[T]) -> str:
        if cls.default_transporter_name is None:
            cls.default_transporter_name = get_default_transporter_name()
        return cls.default_transporter_name

    @classmethod
    def from_http(cls: Type[T], http: HTTPClient) -> T:
        self = cls.__new__(cls)
        self._init_(http)
        return self

    @classmethod
    def from_access_token(cls: Type[T], access_token: str) -> T:
        new_session = new_session_factory(cls.get_default_transporter_name())
        session = new_session()
        http = HTTPClient(session)
        session.headers = http.headers
        authorizer = Authorizer(Token(access_token), None)
        http.authorized_requestor = Authorized(session, authorizer)
        http.requestor = RateLimited(http.authorized_requestor)
        return cls.from_http(http)

    @classmethod
    def from_praw_config(cls: Type[T], site_name: str = '') -> T:
        config = get_praw_config()
        section_name = site_name or config.default_section  # type: ignore[attr-defined]
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
        if 'user_agent' in section:
            self.set_user_agent(get('user_agent'))
        return self

    def __init__(self,
            client_id: str, client_secret: str,
            refresh_token: Optional[str] = None,
            access_token: Optional[str] = None, *,
            username: Optional[str] = None, password: Optional[str] = None,
            grant: Optional[AuthorizationGrant] = None):
        grant_creds = (refresh_token, username, password)
        if grant is None:
            grant = auto_grant_factory(*grant_creds)
            if grant is None:
                raise ValueError("cannot create an authorization grant from the provided credentials")
        elif any(grant_creds):
            raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

        new_session = new_session_factory(self.get_default_transporter_name())
        session = new_session()
        http = HTTPClient(session)
        session.headers = http.headers
        authorizer = Authorizer(
            (None if access_token is None else Token(access_token)),
            TokenObtainmentClient(
                session,
                TOKEN_OBTAINMENT_URL,
                ClientCredentials(client_id, client_secret),
                grant,
            )
        )
        http.authorized_requestor = Authorized(session, authorizer)
        http.requestor = RateLimited(http.authorized_requestor)
        self._init_(http)

    def _init_(self, http: HTTPClient) -> None:
        self.http = http
        self.resource_base_url = RESOURCE_BASE_URL
        self.last_response: Optional[Response] = None
        self.last_response_queue: MutableSequence[Response] = deque(maxlen=12)
        self.last_value: Any = None

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
        ua = self.http.user_agent_string_head
        if s is not None:
            ua += ' Bot -- ' + s
        self.http.user_agent = ua

    def url_join(self, path: str) -> str:
        return self.resource_base_url + path

    async def request(self,
        verb: str,
        path: str,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float = 8,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Any:
        self.last_response = None
        self.last_value = None

        url = self.url_join(path)
        try:
            resp = await self.http.request(verb, url, params=params, payload=payload,
                    data=data, json=json, headers=headers, timeout=timeout, aux_info=aux_info)
        except (
            auth.exceptions.ResponseException,
            http.exceptions.ResponseException,
            core.exceptions.ResponseException,
        ) as e:
            resp = e.response
            self.last_response = resp
            self.last_response_queue.append(resp)
            raise

        self.last_response = resp
        self.last_response_queue.append(resp)

        json_data = None
        if resp.data:
            except_without_context = False
            try:
                json_data = json_loads_response(resp)
            except ValueError:
                except_without_context = True
            if except_without_context:
                raise_for_response_content_error(resp)
                raise_for_status(resp)#_2
                raise UnidentifiedResponseContentError(response=resp)

            self.last_value = json_data

            if isinstance(json_data, Mapping):
                raise_for_json_layout_content_error(resp, json_data)
                raise_for_variant1_reddit_api_error(resp, json_data)
                raise_for_variant2_reddit_api_error(resp, json_data)

        raise_for_status(resp)#_1
        return json_data

    def set_access_token(self, access_token: str) -> None:
        if self.http.authorizer is None:
            raise RuntimeError('The HTTP client does not know of an authorizer instance to assign the token to')
        self.http.authorizer.token = Token(access_token)

class Client(ClientCore):
    def _init_(self, http: HTTPClient) -> None:
        super()._init_(http)
        self.api = ...#site_procedures_ASYNC.SiteProcedures(self)


def c(site_name: str = '') -> Client:
    interactive_mode = not hasattr(__import__('__main__'), '__file__')
    if not interactive_mode:
        raise RuntimeError('function can only be used in interactive mode')

    return Client.from_praw_config(site_name)
