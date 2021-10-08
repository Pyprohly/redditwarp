
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from .typedefs import ClientCredentials, AuthorizationGrant
    from ..http.requestor_SYNC import Requestor

from ..http.request import Request
from ..http.payload import URLEncodedFormData
from ..http.util.json_load import json_loads_response
from .token import Token
from .util import apply_basic_auth
from .exceptions import raise_for_token_server_response_error

class TokenObtainmentClient:
    """The token client will exchange an authorisation grant
    for an OAuth2 token.
    """

    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials,
            grant: AuthorizationGrant):
        self.requestor = requestor
        self.uri = uri
        self.client_credentials = client_credentials
        self.grant = grant

    def fetch_data(self) -> Mapping[str, Any]:
        r = Request('POST', self.uri, payload=URLEncodedFormData(self.grant))
        apply_basic_auth(r, *self.client_credentials)
        resp = self.requestor.send(r)

        try:
            resp_json = json_loads_response(resp)
        except ValueError:
            resp.raise_for_status()
            raise

        raise_for_token_server_response_error(resp_json)
        resp.raise_for_status()
        return resp_json

    def fetch_token(self) -> Token:
        return Token.from_dict(self.fetch_data())
