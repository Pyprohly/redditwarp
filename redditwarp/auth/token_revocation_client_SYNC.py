
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .typedefs import ClientCredentials
    from ..http.requestor_SYNC import Requestor

from ..http.request import make_request
from .utils import apply_basic_auth

class TokenRevocationClient:
    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials):
        self.requestor: Requestor = requestor
        self.uri: str = uri
        self.client_credentials: tuple[str, str] = client_credentials

    def revoke_token(self, token: str, token_type_hint: str = '') -> None:
        data = {'token': token}
        if token_type_hint:
            data['token_type_hint'] = token_type_hint

        r = make_request('POST', self.uri, data=data)
        apply_basic_auth(r, *self.client_credentials)
        resp = self.requestor.send(r)
        resp.raise_for_status()

    def revoke_access_token(self, token: str) -> None:
        self.revoke_token(token, 'access_token')

    def revoke_refresh_token(self, token: str) -> None:
        self.revoke_token(token, 'refresh_token')
