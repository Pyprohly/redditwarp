
from __future__ import annotations
from typing import Mapping, Any

from ..http.util.json_loading import load_json_from_response_but_prefer_status_code_exception_on_failure
from ..auth.token_obtainment_client_ASYNC import TokenObtainmentClient
from ..auth.utils import apply_basic_auth
from .exceptions import raise_for_reddit_token_server_response_error, raise_for_reddit_auth_response_exception

class RedditTokenObtainmentClient(TokenObtainmentClient):
    async def fetch_data(self) -> Mapping[str, Any]:
        headers: dict[str, str] = {}
        apply_basic_auth(headers, *self.client_creds)
        xchg = await self.http.inquire('POST', self.url, headers=headers, data=self.grant)
        resp = xchg.response

        try:
            json_data = load_json_from_response_but_prefer_status_code_exception_on_failure(resp)
            raise_for_reddit_token_server_response_error(json_data)
            resp.ensure_successful_status()

        except Exception as cause:
            try:
                raise_for_reddit_auth_response_exception(cause, xchg)
            except Exception as exc:
                raise exc from cause
            raise

        return json_data
