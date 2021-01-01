
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Optional, Any
if TYPE_CHECKING:
    from .client_credentials import ClientCredentials
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from .token_obtainment_client_SYNC import TokenObtainmentClient
from .exceptions import raise_for_reddit_token_server_response

class RedditTokenObtainmentClient(TokenObtainmentClient):
    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials,
            grant: Mapping[str, Optional[str]],
            headers: Mapping[str, str]):
        super().__init__(requestor, uri, client_credentials, grant)
        self.headers = headers

    def _make_request(self) -> Request:
        r = super()._make_request()
        r.headers.update(self.headers)
        return r

    def _check_response_errors(self, resp: Response, json_dict: Any) -> None:
        raise_for_reddit_token_server_response(resp, json_dict)
