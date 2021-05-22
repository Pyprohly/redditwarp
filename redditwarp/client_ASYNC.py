
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Type, Optional, Mapping, MutableSequence, Union, AnyStr
if TYPE_CHECKING:
    from types import TracebackType
    from .http.response import Response
    from .auth.typedefs import AuthorizationGrant

from .http.util.json_loads import json_loads_response
from .http.transport.ASYNC import new_session
from .auth import Token
from .auth.util import auto_grant_factory
from .auth.reddit_token_obtainment_client_ASYNC import RedditTokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL, RESOURCE_BASE_URL
from .core.http_client_ASYNC import RedditHTTPClient
from .core.authorizer_ASYNC import Authorizer, Authorized
from .core.rate_limited_ASYNC import RateLimited
from .util.praw_config import get_praw_config
from .util.except_without_context_ import except_without_context
from .exceptions import (
    raise_for_status,
    handle_non_json_response,
    raise_for_json_object_data,
)
#from .util.imports import lazy_import;
#if 0: from .site_procedures import ASYNC as site_procedures_ASYNC
#site_procedures_ASYNC = lazy_import('.site_procedures.ASYNC', __package__)  # noqa: F811

class CoreClient:
    T = TypeVar('T', bound='CoreClient')

    @classmethod
    def from_http(cls: Type[T], http: RedditHTTPClient) -> T:
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_access_token(cls: Type[T], access_token: str) -> T:
        session = new_session()
        http = RedditHTTPClient(session)
        token = Token(access_token)
        token_client = None
        authorizer = Authorizer(token, token_client)
        http.authorized_requestor = Authorized(session, authorizer)
        http.requestor = RateLimited(http.authorized_requestor)
        return cls.from_http(http)

    @classmethod
    def from_praw_ini(cls: Type[T], site_name: str) -> T:
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
        if 'user_agent' in section:
            self.set_user_agent(get('user_agent'))
        return self

    @property
    def last_response(self) -> Optional[Response]:
        return self.http.last_response

    @property
    def last_response_queue(self) -> MutableSequence[Response]:
        return self.http.last_response_queue

    def __init__(self,
            client_id: str, client_secret: str,
            refresh_token: Optional[str] = None,
            access_token: Optional[str] = None, *,
            username: Optional[str] = None, password: Optional[str] = None,
            grant: Optional[AuthorizationGrant] = None):
        grant_creds = (refresh_token, username, password)
        if grant is None:
            grant = auto_grant_factory(*grant_creds)
        elif any(grant_creds):
            raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

        session = new_session()
        http = RedditHTTPClient(session)
        token = None if access_token is None else Token(access_token)
        token_client = RedditTokenObtainmentClient(
            session,
            TOKEN_OBTAINMENT_URL,
            (client_id, client_secret),
            grant,
            http.headers,
        )
        authorizer = Authorizer(token, token_client)
        http.authorized_requestor = Authorized(session, authorizer)
        http.requestor = RateLimited(http.authorized_requestor)
        self._init(http)

    def _init(self, http: RedditHTTPClient) -> None:
        self.http = http
        self.resource_base_url = RESOURCE_BASE_URL
        self.last_value: Any = None

    async def __aenter__(self: T) -> T:
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
        path: str,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], AnyStr]] = None,
        json: Any = None,
        timeout: float = -2,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Any:
        url = self.url_join(path)
        resp = await self.http.request(verb, url, params=params, headers=headers,
                data=data, json=json, timeout=timeout, aux_info=aux_info)

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
        if self.http.authorizer is None:
            raise RuntimeError('The HTTP client is missing an authorizer')
        self.http.authorizer.token = Token(access_token)

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_start
        if s is not None:
            ua += ' Bot -- ' + s
        self.http.user_agent = ua

    def url_join(self, path: str) -> str:
        return self.resource_base_url + path

class Client(CoreClient):
    def _init(self, http: RedditHTTPClient) -> None:
        super()._init(http)
        self.api = ...#site_procedures_ASYNC.SiteProcedures(self)
