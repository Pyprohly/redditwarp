
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .types import ClientCredentials
    from ..http.http_client_SYNC import HTTPClient

from .utils import apply_basic_auth

class TokenRevocationClient:
    """Makes token revocation requests."""

    def __init__(self, http: HTTPClient, url: str,
            client_credentials: ClientCredentials) -> None:
        self.http: HTTPClient = http
        self.url: str = url
        self.client_credentials: ClientCredentials = client_credentials

    def revoke_token(self, token: str, token_type_hint: str = '') -> None:
        data = {'token': token}
        if token_type_hint:
            data['token_type_hint'] = token_type_hint

        headers: dict[str, str] = {}
        apply_basic_auth(headers, *self.client_credentials)
        resp = self.http.request('POST', self.url, headers=headers, data=data)
        resp.raise_for_status()

    def revoke_access_token(self, token: str) -> None:
        self.revoke_token(token, 'access_token')

    def revoke_refresh_token(self, token: str) -> None:
        self.revoke_token(token, 'refresh_token')
