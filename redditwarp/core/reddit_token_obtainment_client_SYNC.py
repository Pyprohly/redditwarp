
from __future__ import annotations
from typing import Mapping, Any

from ..http.util.json_load import json_loads_response
from ..auth.token_obtainment_client_SYNC import TokenObtainmentClient
from ..auth.utils import apply_basic_auth
from .exceptions import raise_for_reddit_token_server_response_error, raise_for_reddit_auth_response_exception

class RedditTokenObtainmentClient(TokenObtainmentClient):
    def fetch_data(self) -> Mapping[str, Any]:
        headers: dict[str, str] = {}
        apply_basic_auth(headers, *self.client_creds)
        xchg = self.http.inquire('POST', self.url, headers=headers, data=self.grant)
        resp = xchg.response

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
                raise_for_reddit_auth_response_exception(cause, xchg)
            except Exception as exc:
                raise exc from cause
            raise

        return resp_json
