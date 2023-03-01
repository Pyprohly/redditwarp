
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ...http.http_client_SYNC import HTTPClient
    from ...types import JSON_ro

from ...http.util.json_loading import load_json_from_response_but_prefer_status_code_exception_on_failure
from .token import Token
from ...auth.utils import apply_basic_auth
from .exceptions import raise_for_token_server_response_error
from ..core.const import TOKEN_OBTAINMENT_URL, REDDIT_MOBILE_IOS_CLIENT_ID, GRANT_DATA

class TokenObtainmentClient:
    def __init__(self, http: HTTPClient, url: str,
            client_id: str,
            grant_data: JSON_ro) -> None:
        self.http: HTTPClient = http
        self.url: str = url
        self.client_id: str = client_id
        self.grant_data: JSON_ro = grant_data

    def fetch_data(self) -> Mapping[str, Any]:
        headers: dict[str, str] = {}
        apply_basic_auth(headers, self.client_id, '')
        resp = self.http.request('POST', self.url, headers=headers, json=self.grant_data)

        json_data = load_json_from_response_but_prefer_status_code_exception_on_failure(resp)
        raise_for_token_server_response_error(json_data)
        resp.ensure_successful_status()
        return json_data

    def fetch_token(self) -> Token:
        return Token.from_dict(self.fetch_data())


def new_token_obtainment_client(http: HTTPClient) -> TokenObtainmentClient:
    return TokenObtainmentClient(
        http,
        url=TOKEN_OBTAINMENT_URL,
        client_id=REDDIT_MOBILE_IOS_CLIENT_ID,
        grant_data=GRANT_DATA,
    )
