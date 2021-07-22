
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from .typedefs import ClientCredentials, AuthorizationGrant
    from ..http.requestor_SYNC import Requestor
    from ..http.response import Response

from .. import http
from ..http.request import Request
from ..http.util.json_load import json_loads_response
from ..http.payload import FormData
from .token import ResponseToken
from .util import apply_basic_auth
from .exceptions import (
    ResponseContentError,
    HTTPStatusError,
    raise_for_token_server_response,
)

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

    def _new_request(self) -> Request:
        data = {k: v for k, v in self.grant.items() if v}
        r = Request('POST', self.uri, payload=FormData(data))
        apply_basic_auth(r, self.client_credentials)
        return r

    def _check_response_errors(self, resp: Response, json_dict: Any) -> None:
        raise_for_token_server_response(resp, json_dict)

    def fetch_json_dict(self) -> Mapping[str, Any]:
        r = self._new_request()
        resp = self.requestor.send(r)

        resp_json = None
        try:
            resp_json = json_loads_response(resp)
        except ValueError:
            pass

        if not isinstance(resp_json, Mapping):
            raise ResponseContentError(response=resp)

        self._check_response_errors(resp, resp_json)

        try:
            resp.raise_for_status()
        except http.exceptions.StatusCodeException as e:
            raise HTTPStatusError(response=resp) from e

        return resp_json

    def fetch_token(self) -> ResponseToken:
        return ResponseToken.from_dict(self.fetch_json_dict())
