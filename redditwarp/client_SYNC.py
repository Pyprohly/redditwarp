
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Type, Optional, Mapping, Union, AnyStr
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.typedefs import AuthorizationGrant
    from .http.payload import RequestFiles

from .http.util.json_load import json_loads_response
from .http.transport.SYNC import new_session
from .auth import Token
from .auth.util import auto_grant_factory
from .auth.reddit_token_obtainment_client_SYNC import RedditTokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL
from .core.reddit_http_client_SYNC import RedditHTTPClient
from .core.authorizer_SYNC import Authorizer, Authorized
from .core.rate_limited_SYNC import RateLimited
from .util.praw_config import get_praw_config
from .util.except_without_context import except_without_context
from .exceptions import (
    raise_for_status,
    handle_non_json_response,
    raise_for_json_object_data,
)
from .util.imports import lazy_import;
if 0: from .site_procedures import SYNC as site_procedures_SYNC
site_procedures_SYNC = lazy_import('.site_procedures.SYNC', __package__)  # noqa: F811

class CoreClient:
    """The gateway to interacting with the Reddit API."""

    _USER_AGENT_CUSTOM_DESCRIPTION_SEPARATOR = ' Bot !-- '

    T = TypeVar('T', bound='CoreClient')

    @classmethod
    def from_http(cls: Type[T], http: RedditHTTPClient) -> T:
        """Alternative constructor for testing purposes or advanced uses.

        Parameters
        ----------
        http: Optional[:class:`RedditHTTPClient`]
        """
        self = cls.__new__(cls)
        self._init(http)
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
        session = new_session()
        requestor = RateLimited(
            Authorized(
                session,
                Authorizer(
                    None,
                    Token(access_token),
                ),
            ),
        )
        http = RedditHTTPClient(session, requestor)
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
        elif any(grant_creds):
            raise TypeError("you shouldn't pass grant credentials if you explicitly provide a grant")

        session = new_session()
        token_client = RedditTokenObtainmentClient(
            session,
            TOKEN_OBTAINMENT_URL,
            (client_id, client_secret),
            grant,
        )
        requestor = RateLimited(
            Authorized(
                session,
                Authorizer(
                    token_client,
                    (None if access_token is None else Token(access_token)),
                ),
            ),
        )
        http = RedditHTTPClient(session, requestor)
        token_client.headers = http.headers
        self._init(http)

    def _init(self, http: RedditHTTPClient) -> None:
        self.http = http
        self.last_value: Any = None

    def __enter__(self: T) -> T:
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

    def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], AnyStr]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
    ) -> Any:
        self.last_value = None

        resp = self.http.request(verb, uri, params=params, headers=headers,
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
        """Manually set the access token.

        Tip: the currently set access token can be found with
        `self.http.authorizer.token.access_token`

        Parameters
        ----------
        access_token: str
        """
        if self.http.authorizer is None:
            raise RuntimeError('The HTTP client is missing an authorizer')
        self.http.authorizer.token = Token(access_token)

    def set_user_agent(self, s: Optional[str]) -> None:
        ua = self.http.user_agent_start
        if s is not None:
            ua += self._USER_AGENT_CUSTOM_DESCRIPTION_SEPARATOR + s
        self.http.user_agent = ua

class Client(CoreClient):
    def _init(self, http: RedditHTTPClient) -> None:
        super()._init(http)
        self.p = site_procedures_SYNC.SiteProcedures(self)
