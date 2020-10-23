
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional
if TYPE_CHECKING:
    from .client_credentials import ClientCredentials
    from ..http.requestor_ASYNC import Requestor

from .. import http
from ..http.request import Request
from ..http.util.json_loads import json_loads_response
from ..http.payload import FormData
from .token import ResponseToken
from .util import apply_basic_auth
from .exceptions import (
    ResponseContentError,
    HTTPStatusError,
    raise_for_token_server_response,
)

class TokenObtainmentClient:
    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials,
            grant: Mapping[str, Optional[str]]) -> None:
        self.requestor = requestor
        self.uri = uri
        self.client_credentials = client_credentials
        self.grant = grant

    async def fetch_json_dict(self) -> Mapping[str, Any]:
        data = {k: v for k, v in self.grant.items() if v}
        r = Request('POST', self.uri, payload=FormData(data))
        apply_basic_auth(r, self.client_credentials)

        resp = await self.requestor.send(r)

        resp_json = None
        try:
            resp_json = json_loads_response(resp)
        except ValueError:
            pass

        if not isinstance(resp_json, Mapping):
            raise ResponseContentError(response=resp)

        error = resp_json.get('error')
        if isinstance(error, str):
            raise_for_token_server_response(resp, resp_json)

        try:
            resp.raise_for_status()
        except http.exceptions.StatusCodeException as e:
            raise HTTPStatusError(response=resp) from e

        return resp_json

    async def fetch_token(self) -> ResponseToken:
        return ResponseToken.from_dict(await self.fetch_json_dict())
