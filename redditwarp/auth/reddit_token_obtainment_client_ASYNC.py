
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from .typedefs import ClientCredentials, AuthorizationGrant
    from ..http.requestor_ASYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from .token_obtainment_client_ASYNC import TokenObtainmentClient
from .exceptions import raise_for_reddit_token_server_response

class RedditTokenObtainmentClient(TokenObtainmentClient):
    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials,
            grant: AuthorizationGrant,
            headers: Mapping[str, str]):
        super().__init__(requestor, uri, client_credentials, grant)
        self.headers = headers

    def _new_request(self) -> Request:
        r = super()._new_request()
        r.headers.update(self.headers)
        return r

    def _check_response_errors(self, resp: Response, json_dict: Any) -> None:
        raise_for_reddit_token_server_response(resp, json_dict)
