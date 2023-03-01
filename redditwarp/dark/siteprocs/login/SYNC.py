
from __future__ import annotations
from typing import Optional, Iterable

import time
import json
import re

from ....core.http_client_SYNC import HTTPClient
from ....http.util.json_loading import load_json_from_response_but_prefer_status_code_exception_on_failure
from ....exceptions import (
    OperationException,
    raise_for_reddit_error,
)
from ....util.redditwarp_installed_client_credentials import get_device_id
from ...util.request_signing import (
    SIGNATURE_UA_MESSAGE_TEMPLATE,
    SIGNATURE_BODY_MESSAGE_TEMPLATE,
    generate_hmac_hash,
    generate_android_mobile_hmac_hash,
    get_android_mobile_request_signature,
)


class LoginProcedures:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    def do_legacy_web_login(self, username: str, password: str, otp: Optional[str] = None) -> tuple[str, str]:
        def g() -> Iterable[tuple[str, str]]:
            yield ('user', username)
            yield ('passwd', password)
            if otp is not None: yield ('otp', otp)

        resp = self._http.request(
                'POST', 'https://old.reddit.com/api/login',
                params={'api_type': 'json'},
                headers={'User-Agent': self._http.get_user_agent()},
                data=dict(g()))

        json_data = load_json_from_response_but_prefer_status_code_exception_on_failure(resp)

        raise_for_reddit_error(json_data)

        d = json_data['json']['data']
        if d.get('details', '') == 'TWO_FA_REQUIRED':
            raise OperationException('TWO_FA_REQUIRED')

        resp.ensure_successful_status()

        return (d['cookie'], d['modhash'])

    def do_modern_web_login(self, username: str, password: str, otp: Optional[str] = None) -> None:
        headers = {'User-Agent': self._http.get_user_agent()}

        resp = self._http.request('GET', 'https://www.reddit.com/login/', headers=headers)
        resp.ensure_successful_status()

        body = resp.data.decode()
        m = re.search(r'''<input type="hidden" name="csrf_token" value="(\w+)">''', body)
        if m is None:
            raise RuntimeError
        csrf_token = m[1]

        def g() -> Iterable[tuple[str, str]]:
            yield ('csrf_token', csrf_token)
            yield ('username', username)
            yield ('password', password)
            if otp is not None: yield ('otp', otp)

        resp = self._http.request('POST', 'https://www.reddit.com/login', headers=headers, data=dict(g()))

        json_data = load_json_from_response_but_prefer_status_code_exception_on_failure(resp)

        raise_for_reddit_error(json_data)

        if json_data.get('details', '') == 'TWO_FA_REQUIRED':
            raise OperationException('TWO_FA_REQUIRED')

        resp.ensure_successful_status()

    def do_android_mobile_login(self, username: str, password: str, otp: Optional[str] = None) -> tuple[int, str]:
        epoch = int(time.time())
        ua = self._http.get_user_agent()
        vendor = get_device_id()

        msg = SIGNATURE_UA_MESSAGE_TEMPLATE % (epoch, ua, vendor)
        hsh = generate_android_mobile_hmac_hash(msg)
        ua_sig = get_android_mobile_request_signature(epoch, hsh)

        body_obj = {
            "username": username,
            "password": password,
            **({} if otp is None else {"otp": otp}),
        }
        body = json.dumps(body_obj, separators=(',', ':'))
        msg = SIGNATURE_BODY_MESSAGE_TEMPLATE % (epoch, body)
        hsh = generate_android_mobile_hmac_hash(msg)
        body_sig = get_android_mobile_request_signature(epoch, hsh)

        resp = self._http.request(
                'POST', 'https://accounts.reddit.com/api/login',
                headers={
                    'User-Agent': ua,
                    'client-vendor-id': vendor,
                    'X-hmac-signed-result': ua_sig,
                    'X-hmac-signed-body': body_sig,
                },
                data=body.encode())

        json_data = load_json_from_response_but_prefer_status_code_exception_on_failure(resp)

        raise_for_reddit_error(json_data.get('error'))

        resp.ensure_successful_status()

        _, _, user_id36 = json_data['userId'].partition('_')
        return (int(user_id36, 36), json_data['modhash'])
