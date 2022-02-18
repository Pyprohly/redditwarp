
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...http.util.json_load import json_loads_response
from ...exceptions import (
    ClientException,
    UnexpectedResultException,
    raise_for_reddit_error,
    raise_for_non_json_response,
)


class SiteProcedures:
    def __init__(self, client: Client):
        self._client = client

    def do_legacy_reddit_web_login(self, username: str, password: str, otp: str = '') -> tuple[str, str]:
        http = self._client.dark_http
        resp = http.session.request(
                'POST',
                'https://www.reddit.com/api/login',
                params={'api_type': 'json'},
                headers={
                    'User-Agent': http.headers['User-Agent'],
                    # I don't understand why but the request fails with a `WRONG_PASSWORD` API error if
                    # it includes the `User-Agent` header, but adding some other random header fixes it.
                    'asdf': 'asdf',
                },
                data={'user': username, 'passwd': password, 'otp': otp})

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
            raise ClientException('TWO_FA_REQUIRED')
        elif details:
            raise UnexpectedResultException(json_data)

        return (d['cookie'], d['modhash'])

    def get_sendbird_access_token(self) -> tuple[str, float]:
        d = self._client.dark_request('GET', 'https://sendbird.reddit.com/api/v1/sendbird/me')
        access_token = d['sb_access_token']
        expires_ts = d['valid_until'] / 1000
        return (access_token, expires_ts)
