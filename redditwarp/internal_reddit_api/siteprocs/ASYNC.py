
from __future__ import annotations

from ...core.http_client_ASYNC import HTTPClient
from ...http.util.json_load import json_loads_response
from ...exceptions import (
    OperationException,
    raise_for_reddit_error,
    raise_for_non_json_response,
)


class Procedures:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    async def do_legacy_reddit_web_login(self, username: str, password: str, otp: str = '') -> tuple[str, str]:
        resp = await self._http.request(
                'POST',
                'https://www.reddit.com/api/login',
                params={'api_type': 'json'},
                headers={
                    'User-Agent': self._http.get_user_agent(),
                    # I don't understand why but the request fails with a `WRONG_PASSWORD` API error if
                    # it includes the `User-Agent` header, but adding some other random header fixes it.
                    'asdf': 'asdf',
                },
                data={'user': username, 'passwd': password, 'otp': otp})
        resp.raise_for_status()

        try:
            json_data = json_loads_response(resp)
        except ValueError as cause:
            try:
                raise_for_non_json_response(resp)
            except Exception as exc:
                raise exc from cause
            raise

        raise_for_reddit_error(json_data)

        d = json_data['json']['data']
        details = d.get('details', '')
        if details == 'TWO_FA_REQUIRED':
            raise OperationException('TWO_FA_REQUIRED')

        return (d['cookie'], d['modhash'])

    async def get_sendbird_access_token(self) -> tuple[str, float]:
        resp = await self._http.request('GET', 'https://sendbird.reddit.com/api/v1/sendbird/me')
        resp.raise_for_status()
        d = json_loads_response(resp)
        access_token = d['sb_access_token']
        expires_utms = d['valid_until']
        expires_ts = expires_utms / 1000
        return (access_token, expires_ts)
