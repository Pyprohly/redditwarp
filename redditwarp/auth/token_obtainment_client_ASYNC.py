
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from .types import ClientCredentials, AuthorizationGrant
    from ..http.http_client_ASYNC import HTTPClient

from ..http.util.json_load import json_loads_response
from .token import Token
from .utils import apply_basic_auth
from .exceptions import raise_for_token_server_response_error

class TokenObtainmentClient:
    def __init__(self, http: HTTPClient, url: str,
            client_credentials: ClientCredentials,
            grant: AuthorizationGrant) -> None:
        self.http: HTTPClient = http
        self.url: str = url
        self.client_credentials: ClientCredentials = client_credentials
        self.grant: Mapping[str, str] = grant

    async def fetch_data(self) -> Mapping[str, Any]:
        headers: dict[str, str] = {}
        apply_basic_auth(headers, *self.client_credentials)
        resp = await self.http.request('POST', self.url, data=self.grant, headers=headers)

        try:
            resp_json = json_loads_response(resp)
        except ValueError:
            resp.raise_for_status()
            raise

        raise_for_token_server_response_error(resp_json)
        resp.raise_for_status()
        return resp_json

    async def fetch_token(self) -> Token:
        return Token.from_dict(await self.fetch_data())
