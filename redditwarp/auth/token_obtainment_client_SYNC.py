
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
    """The token client exchanges an authorisation grant for an OAuth2 token."""

    def __init__(self, http: HTTPClient, url: str,
            client_creds: ClientCredentials,
            grant: AuthorizationGrant) -> None:
        self.http: HTTPClient = http
        self.url: str = url
        self.client_creds: ClientCredentials = client_creds
        self.grant: AuthorizationGrant = grant

    def fetch_data(self) -> Mapping[str, Any]:
        """Exchange an authorisation grant for an OAuth2 token.

        .. RETURNS

        :returns:
            OAuth2 token data.
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
        """
        Call :meth:`self.fetch_data <.fetch_data>` and construct a
        :class:`~.redditwarp.auth.token.Token` from it.
        """
        return Token.from_dict(self.fetch_data())
