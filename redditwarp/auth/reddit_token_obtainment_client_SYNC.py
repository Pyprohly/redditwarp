
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Optional
if TYPE_CHECKING:
    from .client_credentials import ClientCredentials
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request

from .token_obtainment_client_SYNC import TokenObtainmentClient

class RedditTokenObtainmentClient(TokenObtainmentClient):
    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials,
            grant: Mapping[str, Optional[str]],
            headers: Mapping[str, str]):
        super().__init__(requestor, uri, client_credentials, grant)
        self.headers = headers

    def make_request(self) -> Request:
        r = super().make_request()
        r.headers.update(self.headers)
        return r
