
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .typedefs import ClientCredentials
    from ..http.requestor_SYNC import Requestor

from ..http.request import Request
from ..http.payload import URLEncodedFormData
from .util import apply_basic_auth
from .exceptions import raise_for_status

class TokenRevocationClient:
    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials):
        self.requestor = requestor
        self.uri = uri
        self.client_credentials = client_credentials

    def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
        data = {'token': token}
        if token_type_hint:
            data['token_type_hint'] = token_type_hint

        r = Request('POST', self.uri, payload=URLEncodedFormData(data))
        apply_basic_auth(r, self.client_credentials)

        resp = self.requestor.send(r)

        raise_for_status(resp)

    def revoke_access_token(self, token: str) -> None:
        self.revoke_token(token, 'access_token')

    def revoke_refresh_token(self, token: str) -> None:
        self.revoke_token(token, 'refresh_token')
