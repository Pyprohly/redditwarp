
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from .types import ClientCredentials, AuthorizationGrant
    from ..http.http_client_ASYNC import HTTPClient

from ..http.util.json_loading import load_json_from_response_but_prefer_status_code_exception_on_failure
from .token import Token
from .utils import apply_basic_auth
from .exceptions import raise_for_token_server_response_error

class TokenObtainmentClient:
    def __init__(self, http: HTTPClient, url: str,
            client_creds: ClientCredentials,
            grant: AuthorizationGrant) -> None:
        self.http: HTTPClient = http
        self.url: str = url
        self.client_creds: ClientCredentials = client_creds
        self.grant: AuthorizationGrant = grant

    async def fetch_data(self) -> Mapping[str, Any]:
        headers: dict[str, str] = {}
        apply_basic_auth(headers, *self.client_creds)
        resp = await self.http.request('POST', self.url, data=self.grant, headers=headers)

        json_data = load_json_from_response_but_prefer_status_code_exception_on_failure(resp)
        raise_for_token_server_response_error(json_data)
        resp.ensure_successful_status()
        return json_data

    async def fetch_token(self) -> Token:
        return Token.from_dict(await self.fetch_data())
