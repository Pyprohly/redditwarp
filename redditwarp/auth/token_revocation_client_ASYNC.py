
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .types import ClientCredentials
    from ..http.http_client_ASYNC import HTTPClient

from .utils import apply_basic_auth

class TokenRevocationClient:
    """Makes token revocation requests."""

    def __init__(self, http: HTTPClient, url: str,
            client_creds: ClientCredentials) -> None:
        """
        .. .PARAMETERS

        :param http: An instance of an HTTP client to make the requests.
        :type http: :class:`~.http.http_client_ASYNC.HTTPClient`
        :param url: The URL of the revocation endpoint.
        :type url: str
        :param client_creds: The client credentials to be used in the revocation request.
        :type client_creds: :data:`~.types.ClientCredentials`
        """
        self.http: HTTPClient = http
        self.url: str = url
        self.client_creds: ClientCredentials = client_creds

    async def revoke_token(self, token: str, token_type_hint: str = '') -> None:
        """Makes a revocation request for a token.

        .. .PARAMETERS

        :param token: The token to be revoked.
        :type token: str
        :param token_type_hint: A hint about the type of the token
            (e.g. `access_token`, `refresh_token`).
            This is supposed to make the operation slightly quicker for
            the server. If the given hint is invalid then the server
            should still attempt to resolve and revoke the token.
        :type token_type_hint: str
        """
        data = {'token': token}
        if token_type_hint:
            data['token_type_hint'] = token_type_hint

        headers: dict[str, str] = {}
        apply_basic_auth(headers, *self.client_creds)
        resp = await self.http.request('POST', self.url, headers=headers, data=data)
        resp.ensure_successful_status()

    async def revoke_access_token(self, token: str) -> None:
        """Makes a revocation request for an access token.

        Calls `self.revoke_token(token, 'access_token')`.

        .. .PARAMETERS

        :param token: The access token to be revoked.
        :type token: str
        """
        await self.revoke_token(token, 'access_token')

    async def revoke_refresh_token(self, token: str) -> None:
        """Makes a revocation request for a refresh token.

        Calls `self.revoke_token(token, 'refresh_token')`.

        .. .PARAMETERS

        :param token: The refresh token to be revoked.
        :type token: str
        """
        await self.revoke_token(token, 'refresh_token')
