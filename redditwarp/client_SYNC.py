
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Optional, Mapping, Union, Callable, overload
if TYPE_CHECKING:
    from types import TracebackType
    from .auth.types import AuthorizationGrant
    from .http.types import RequestFiles
    from .core.http_client_SYNC import HTTPClient
    from .types import JSON_ro

from .auth import Token
from .auth import grants
from .core import grants as core_grants
from .core.http_client_SYNC import (
    RedditHTTPClient,
    build_reddit_http_client,
    build_reddit_http_client_from_access_token,
)
from .exceptions import raise_for_reddit_error, raise_for_non_json_response
from .http.util.json_load import json_loads_response
from .util.redditwarp_installed_client_credentials import get_redditwarp_client_id, get_device_id


class Client:
    """Gateway to interacting with the Reddit API."""

    _TSelf = TypeVar('_TSelf', bound='Client')

    @staticmethod
    def from_praw_config(section_name: str, *, filepath: Optional[str] = None) -> Client:
        """Initialize a `Client` instance from a `praw.ini` file.

        This method aims to replicate the single-argument form of PRAW's `Reddit`
        class constructor. If `filepath` is not specified it will search for
        `praw.ini` files in the same locations PRAW does.

        Only a subset of PRAW's configuration keys are read:

        * `client_id`
        * `client_secret`
        * `refresh_token`
        * `username`
        * `password`
        * `user_agent`

        The credential values are given directly to the `Client` constructor,
        then the `user_agent` value (if present) is passed to :meth:`.set_user_agent`.

        .. .PARAMETERS

        :param section_name:
            The section name of the ini file in which to read values from.
            Pass an empty string to use the default section name "`DEFAULT`".
        :param filepath:
            The location of a `praw.ini` file to read.

            If not specified, the locations returned by
            :func:`redditwarp.util.praw_config.get_praw_ini_potential_locations`
            are searched and any files found are read and combined into a single
            configuration.
        """
        from .util.praw_config_SYNC import client_from_praw_config  # Avoid cyclic import
        return client_from_praw_config(section_name, filepath=filepath)

    @classmethod
    def from_http(cls: type[_TSelf], http: HTTPClient) -> _TSelf:
        """Alternative constructor for testing purposes or advanced use cases."""
        self = cls.__new__(cls)
        self._init(http)
        return self

    @classmethod
    def from_access_token(cls: type[_TSelf], access_token: str) -> _TSelf:
        """Construct an instance without a token client.

        No token client means `self.http.authorizer.token_client` will be `None`.

        When the access token becomes invalid you'll need to deal with the
        401 Unauthorized :class:`~redditwarp.http.exceptions.StatusCodeException`
        exception that will be thrown upon making API requests.

        Use the :meth:`.set_access_token` method to assign new access tokens.
        """
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
        """
        .. .PARAMETERS

        :param client_id:
        :param client_secret:
        :param refresh_token:
        :param username:
        :param password:
        :param grant:
            Specify an explicit grant. Use this parameter if you want to limit
            authorization scopes, or if you need to use the Installed Client grant type.

        If `client_id` and `client_secret` are the only credentials given then a
        Client Credentials grant will be configured. The client will effectively
        be in a read-only mode.
        """
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
        from .siteprocs.SYNC import SiteProcedures
        self.p: SiteProcedures = SiteProcedures(self)

    def __enter__(self: _TSelf) -> _TSelf:
        return self

    def __exit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Calls `self.close()`"""
        self.close()
        return None

    def close(self) -> None:
        """Calls `self.http.close()`"""
        self.http.close()

    def request(self,
        verb: str,
        url: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: JSON_ro = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
        snub: Optional[Callable[[JSON_ro], None]] = raise_for_reddit_error,
    ) -> Any:
        """Make an API request and return JSON data.

        The parameters are similar to
        :meth:`redditwarp.http.http_client_SYNC.HTTPClient.request`,
        except for `snub`.

        The `snub` function examines the returned JSON data for API problems and
        generates exceptions based on them. You may choose to assign this option
        if you implement an API endpoint and know the structure of the errors,
        but the default snub function covers most Reddit API error structures.

        This method is only appropriate for making calls to the Reddit API
        and not any other website because of the domain specific post processing
        that happens with the response data.

        .. .RAISES

        :raises ValueError:
            The endpoint did not return JSON data.
        :raises redditwarp.http.exceptions.StatusCodeException:
            The API call returned a non 2XX status code.
        :raises redditwarp.exceptions.RedditError:
            The `snub` function detected an API error.
        """
        json_data = None
        try:
            resp = self.http.request(verb, url, params=params, headers=headers,
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
        """Manually set the current access token."""
        http = self.http
        if not isinstance(http, RedditHTTPClient):
            raise RuntimeError(f"self.http must be {RedditHTTPClient.__name__}")
        http.authorizer.set_token(Token(access_token))

    def set_user_agent(self, s: Optional[str]) -> None:
        """Set a user agent description.

        To view or set the current user agent string directly,
        use `self.http.get_user_agent()`.
        """
        ua = self.http.user_agent_base
        if s is not None:
            ua = f"{ua} Bot !-- {s}"
        self.http.set_user_agent(ua)

RedditClient = Client
Reddit = Client
RedditWarp = Client
