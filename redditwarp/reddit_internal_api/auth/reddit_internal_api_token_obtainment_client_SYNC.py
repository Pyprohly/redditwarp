
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ...http.requestor_SYNC import Requestor

from ...http.request import make_request
from ...http.util.json_load import json_loads_response
from .token import Token
from ...auth.utils import apply_basic_auth
from .exceptions import raise_for_token_server_response_error
from .const import TOKEN_OBTAINMENT_URL, REDDIT_MOBILE_IOS_CLIENT_ID, GRANT_DATA

class RedditInternalAPITokenObtainmentClient:
    def __init__(self, requestor: Requestor, uri: str,
            client_id: str,
            grant_data: Any):
        self.requestor: Requestor = requestor
        self.uri: str = uri
        self.client_id: str = client_id
        self.grant_data: Any = grant_data

    def fetch_data(self) -> Mapping[str, Any]:
        r = make_request('POST', self.uri, json=self.grant_data)
        apply_basic_auth(r, self.client_id, '')
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


def new_reddit_internal_api_token_obtainment_client(requestor: Requestor) -> RedditInternalAPITokenObtainmentClient:
    return RedditInternalAPITokenObtainmentClient(
        requestor,
        uri=TOKEN_OBTAINMENT_URL,
        client_id=REDDIT_MOBILE_IOS_CLIENT_ID,
        grant_data=GRANT_DATA,
    )
