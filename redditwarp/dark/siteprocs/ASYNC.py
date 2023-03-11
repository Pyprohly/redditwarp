
from __future__ import annotations

from ...core.http_client_ASYNC import HTTPClient
from ...http.util.json_loading import load_json_from_response
from .login.ASYNC import LoginProcedures


class Procedures:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http
        self.login: LoginProcedures = LoginProcedures(http)
        ("")

    async def ping(self) -> None:
        await self._http.request('GET', 'https://oauth.reddit.com/api/v1/scopes', params={'scopes': 'read'})

    async def get_sendbird_access_token(self) -> tuple[str, int]:
        resp = await self._http.request('GET', 'https://sendbird.reddit.com/api/v1/sendbird/me')
        resp.ensure_successful_status()
        d = load_json_from_response(resp)
        access_token = d['sb_access_token']
        expires_utms = d['valid_until']
        expires_ts = expires_utms // 1000
        return (access_token, expires_ts)
