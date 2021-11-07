
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Optional, Mapping, Union
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.typedefs import ClientCredentials, AuthorizationGrant
    from .http.payload import RequestFiles

from .http.util.json_load import json_loads_response
from .http.transport.SYNC import new_session
from .auth import Token
from .auth.util import auto_grant_factory
from .core.reddit_token_obtainment_client_SYNC import RedditTokenObtainmentClient
from .auth.const import TOKEN_OBTAINMENT_URL
from .core.reddit_http_client_SYNC import RedditHTTPClient
from .core.authorizer_SYNC import Authorizer, Authorized
from .core.rate_limited_SYNC import RateLimited
from .core.recorded_SYNC import Recorded, Last
from .util.praw_config import get_praw_config
from .exceptions import raise_for_non_json_response, raise_for_reddit_error

class CoreClient:
    """The gateway to interacting with the Reddit API."""

    _USER_AGENT_CUSTOM_DESCRIPTION_SEPARATOR = ' Bot !-- '
    _TSelf = TypeVar('_TSelf', bound='CoreClient')

    @classmethod
    def from_creds(cls: type[_TSelf], client_creds: ClientCredentials, grant: AuthorizationGrant) -> _TSelf:
        return cls(*client_creds, grant=grant)

    @classmethod
    def from_http(cls: type[_TSelf], http: RedditHTTPClient) -> _TSelf:
        """Alternative constructor for testing purposes or advanced uses.

        Parameters
        ----------
        http: Optional[:class:`RedditHTTPClient`]
        """
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_access_token(cls: type[_TSelf], access_token: str) -> _TSelf:
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
        """
        Parameters
        ----------
        client_id: str
        client_secret: str
            If you've registered an installed app (hence using the :class:`~.InstalledClient`
            grant type) you won't be given a client secret. The Reddit docs say to use an
            empty string in this case.
        refresh_token: Optional[str]
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

    def __enter__(self: _TSelf) -> _TSelf:
        return self

    def __exit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def close(self) -> None:
        self.http.close()

    def request(self,
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
        json_data = None
        try:
            resp = self.http.request(verb, uri, params=params, headers=headers,
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

                raise_for_reddit_error(json_data)
        finally:
            self.last_value = json_data

        resp.raise_for_status()
        return json_data

    def set_access_token(self, access_token: str) -> None:
        """Manually set the current access token.

        Tip: the current access token is found at
        `self.http.authorizer.token.access_token`

        Parameters
        ----------
        access_token: str
        """
        self.http.authorizer.token = Token(access_token)

    def set_user_agent(self, s: Optional[str]) -> None:
        """Set a customer user agent description.

        To view or set the current user agent string, see `self.http.user_agent`."""
        ua = self.http.user_agent_lead
        if s is not None:
            ua += self._USER_AGENT_CUSTOM_DESCRIPTION_SEPARATOR + s
        self.http.user_agent = ua

class Client(CoreClient):
    def _init(self, http: RedditHTTPClient) -> None:
        super()._init(http)
        from .siteprocs.SYNC import SiteProcedures
        self.p: SiteProcedures = SiteProcedures(self)
