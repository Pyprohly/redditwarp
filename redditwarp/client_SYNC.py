
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Type, Optional, Mapping, MutableSequence
if TYPE_CHECKING:
    from types import TracebackType
    from .http.payload import Payload
    from .http.response import Response

from collections import deque

from . import http
from .http.util.json_loads import json_loads_response
from .http.transport.SYNC import get_default_transporter_name, new_session_factory
from . import auth
from .auth import ClientCredentials, Token
from .auth.util import auto_grant_factory
from .auth.token_obtainment_client_SYNC import TokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL, RESOURCE_BASE_URL
from . import core
from .core.http_client_SYNC import HTTPClient
from .core.authorizer_SYNC import Authorizer, Authorized
from .core.ratelimited_SYNC import RateLimited
from .util.praw_config import get_praw_config
from .exceptions import (
    UnidentifiedResponseContentError,
    raise_for_status,
    raise_for_response_content_error,
    raise_for_json_layout_content_error,
    raise_for_variant1_reddit_api_error,
    raise_for_variant2_reddit_api_error,
)
from .util.module_importing import lazy_import;
if 0: from .api.site_procedures import SYNC as site_procedures_SYNC
site_procedures_SYNC = lazy_import('.api.site_procedures.SYNC', __package__)  # noqa: F811

AuthorizationGrant = Mapping[str, Optional[str]]

class ClientCore:
    """The gateway to interacting with the Reddit API."""

    default_transporter_name = None

    T = TypeVar('T', bound='ClientCore')

    @classmethod
    def get_default_transporter_name(cls: Type[T]) -> str:
        if cls.default_transporter_name is None:
            cls.default_transporter_name = get_default_transporter_name()
        return cls.default_transporter_name

    @classmethod
    def from_http(cls: Type[T], http: HTTPClient) -> T:
        """Alternative constructor for testing purposes or advanced uses.

        Parameters
        ----------
        http: Optional[:class:`HTTPClient`]
        """
        self = cls.__new__(cls)
        self._init_(http)
        return self

    @classmethod
    def from_access_token(cls: Type[T], access_token: str) -> T:
        """Construct a Reddit client instance without a token client.

        No token client means `self.http.authorizer.token_client` will be `None`.

        When the token becomes invalid you'll need to deal with the 401 Unauthorized
        exception that will be thrown upon making requests. You can use the
        :meth:`set_access_token` instance method to assign a new token.

        Parameters
        ----------
        access_token: str
        """
        new_session = new_session_factory(cls.get_default_transporter_name())
        session = new_session()
        http = HTTPClient(session)
        session.headers = http.headers
        authorizer = Authorizer(Token(access_token), None)
        http.authorized_requestor = Authorized(session, authorizer)
        http.requestor = RateLimited(http.authorized_requestor)
        return cls.from_http(http)

    @classmethod
    def from_praw_config(cls: Type[T], site_name: str) -> T:
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
        """
        Parameters
        ----------
        client_id: str
        client_secret: str
            If you've registered an installed app (hence using the :class:`~.InstalledClient`
            grant type) you won't be given a client secret. The Reddit docs say to use an
            empty string in this case.
        refresh_token: Optional[str]
        access_token: Optional[str]
            Initialize the client :class:`~.Authorizer` with an access token.
            The token will continue to be used until the server indicates
            an invalid token, in which case the configured grant will used to
            exchange for a new access token.
        username: Optional[str]
            Reddit account username.
            Must be used with :param:`password`.
            Ignored if :param:`refresh_token` is used.
        password: Optional[str]
            Reddit account password.
            Must be used with :param:`username`.
            Ignored if :param:`refresh_token` is used.
        grant: Optional[:class:`~.AuthorizationGrant`]
            Explicitly input a grant. Use this parameter if you need to limit
            authorization scopes, or if you need to use the Installed Client grant type.

        A :class:`~.ClientCredentialsGrant` grant will be configured if only :param:`client_id`
        and :param:`client_secret` are specified.

        Raises
        ------
        TypeError
            If grant credential parameters were specified and the `grant` parameter was used.
        ValueError
            You used :param:`username` without :param:`password` or vice versa.
        """
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

    def __enter__(self) -> ClientCore:
        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def close(self) -> None:
        self.http.close()

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_string_head
        if s is not None:
            ua += ' Bot -- ' + s
        self.http.user_agent = ua

    def url_join(self, path: str) -> str:
        return self.resource_base_url + path

    def request(self,
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
            resp = self.http.request(verb, url, params=params, payload=payload,
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
        """Manually set the access token.

        Tip: the currently set access token can be found with
        `self.http.authorizer.token.access_token`

        Parameters
        ----------
        access_token: str
        """
        if self.http.authorizer is None:
            raise RuntimeError('The HTTP client does not know of an authorizer instance to assign the token to')
        self.http.authorizer.token = Token(access_token)

class Client(ClientCore):
    def _init_(self, http: HTTPClient) -> None:
        super()._init_(http)
        self.api = site_procedures_SYNC.SiteProcedures(self)
