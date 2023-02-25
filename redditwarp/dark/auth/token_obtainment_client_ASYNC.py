
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ...http.http_client_ASYNC import HTTPClient
    from ...types import JSON_ro

from ...http.util.json_load import json_loads_response
from .token import Token
from ...auth.utils import apply_basic_auth
from .exceptions import raise_for_token_server_response_error
from .const import TOKEN_OBTAINMENT_URL, REDDIT_MOBILE_IOS_CLIENT_ID, GRANT_DATA

class TokenObtainmentClient:
    def __init__(self, http: HTTPClient, url: str,
            client_id: str,
            grant_data: JSON_ro) -> None:
        self.http: HTTPClient = http
        self.url: str = url
        self.client_id: str = client_id
        self.grant_data: JSON_ro = grant_data

    async def fetch_data(self) -> Mapping[str, Any]:
        headers: dict[str, str] = {}
        apply_basic_auth(headers, self.client_id, '')
        resp = await self.http.request('POST', self.url, headers=headers, json=self.grant_data)

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


def new_token_obtainment_client(http: HTTPClient) -> TokenObtainmentClient:
    return TokenObtainmentClient(
        http,
        url=TOKEN_OBTAINMENT_URL,
        client_id=REDDIT_MOBILE_IOS_CLIENT_ID,
        grant_data=GRANT_DATA,
    )
