
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional
if TYPE_CHECKING:
    from ..auth.typedefs import ClientCredentials, AuthorizationGrantType as AuthorizationGrant
    from ..http.requestor_ASYNC import Requestor

from ..http.request import make_request
from ..http.util.json_load import json_loads_response
from ..auth.token_obtainment_client_ASYNC import TokenObtainmentClient
from ..auth.utils import apply_basic_auth
from .exceptions import raise_for_reddit_token_server_response_error, raise_for_reddit_auth_response_exception

class RedditTokenObtainmentClient(TokenObtainmentClient):
    def __init__(self, requestor: Requestor, uri: str,
            client_credentials: ClientCredentials,
            grant: AuthorizationGrant,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor, uri, client_credentials, grant)
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def fetch_data(self) -> Mapping[str, Any]:
        r = make_request('POST', self.uri, data=self.grant)
        apply_basic_auth(r, *self.client_credentials)
        r.headers.update(self.headers)
        resp = await self.requestor.send(r)

        try:
            try:
                resp_json = json_loads_response(resp)
            except ValueError as cause:
                try:
                    resp.raise_for_status()
                except Exception as exc:
                    raise exc from cause
                raise

            raise_for_reddit_token_server_response_error(resp_json)
            resp.raise_for_status()

        except Exception as cause:
            try:
                raise_for_reddit_auth_response_exception(cause, r, resp)
            except Exception as exc:
                raise exc from cause
            raise

        return resp_json
