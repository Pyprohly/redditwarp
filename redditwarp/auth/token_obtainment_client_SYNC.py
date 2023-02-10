
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from .types import ClientCredentials, AuthorizationGrant
    from ..http.http_client_SYNC import HTTPClient

from ..http.util.json_load import json_loads_response
from .token import Token
from .utils import apply_basic_auth
from .exceptions import raise_for_token_server_response_error

class TokenObtainmentClient:
    """Exchanges an authorisation grant for an OAuth2 token."""

    def __init__(self, http: HTTPClient, url: str,
            client_creds: ClientCredentials,
            grant: AuthorizationGrant) -> None:
        """
        .. .PARAMETERS

        :param http:
            An instance of `HTTPClient` class that makes the HTTP requests.
        :type http:
            :class:`~.http.http_client_SYNC.HTTPClient`
        :param url:
            The token obtainment endpoint URL to make the request to.
        :type url:
            str
        :param client_creds:
            The client credentials to use.
        :type client_creds:
            :data:`~.types.ClientCredentials`
        :param grant:
            An authorization grant.
        :type grant:
            :data:`~.types.AuthorizationGrant`
        """
        self.http: HTTPClient = http
        self.url: str = url
        self.client_creds: ClientCredentials = client_creds
        self.grant: AuthorizationGrant = grant

    def fetch_data(self) -> Mapping[str, Any]:
        """Exchange an authorisation grant for OAuth2 token data.

        Makes a POST request to the specified URL (:attr:`url`) with
        the provided client credentials (:attr:`client_creds`) and
        authorization grant (:attr:`grant`).

        .. .RETURNS

        :returns:
            A dictionary of OAuth2 token data.
        :rtype: Mapping[str, Any]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            The response from the server is not a success status code.
        :raises ValueError:
            The response from the server cannot be parsed as JSON.
        """
        headers: dict[str, str] = {}
        apply_basic_auth(headers, *self.client_creds)
        resp = self.http.request('POST', self.url, data=self.grant, headers=headers)

        try:
            resp_json = json_loads_response(resp)
        except ValueError:
            resp.raise_for_status()
            raise

        raise_for_token_server_response_error(resp_json)
        resp.raise_for_status()
        return resp_json

    def fetch_token(self) -> Token:
        """Obtain a `Token` instance.

        Makes use of the :meth:`.fetch_data` method to obtain OAuth2 token
        data and then constructs a :class:`~redditwarp.auth.token.Token` instance from the obtained data.

        .. .RETURNS

        :returns:
            An instance of the `Token` class representing the obtained OAuth2 token.
        :rtype: :class:`~redditwarp.auth.token.Token`
        """
        return Token.from_dict(self.fetch_data())
