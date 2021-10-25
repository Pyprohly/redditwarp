
from __future__ import annotations

import pytest

from redditwarp import http
from redditwarp import auth
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.core.exceptions import raise_for_reddit_auth_response_exception
from redditwarp.core import exceptions

def test_incorrect_access_token_url() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://reddit.com/api/v1/access_token')
    resp = Response(401, {}, b'')
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.match('token URL')

def test_no_authorization_header() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://www.reddit.com/api/v1/access_token')
    resp = Response(401, {}, b'')
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.match('Authorization')

def test_authorization_header_no_basic() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://www.reddit.com/api/v1/access_token', headers={'Authorization': 'asdf'})
    resp = Response(401, {}, b'')
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.match('Basic')

def test_BlacklistedUserAgent() -> None:
    exc = http.exceptions.StatusCodeException(status_code=403)
    req = Request('', '', headers={'User-Agent': 'xscrapingx'})
    resp = Response(403, {}, b'<!doctype html>')
    with pytest.raises(exceptions.BlacklistedUserAgent):
        raise_for_reddit_auth_response_exception(exc, req, resp)

def test_CredentialsError() -> None:
    exc: Exception = auth.exceptions.TokenServerResponseErrorTypes.InvalidGrant(error_name='invalid_grant')
    req = Request('', '')
    resp = Response(400, {}, b'{"error": "invalid_grant"}')
    with pytest.raises(exceptions.GrantCredentialsError):
        raise_for_reddit_auth_response_exception(exc, req, resp)

    exc = auth.exceptions.TokenServerResponseErrorTypes.InvalidGrant(error_name='invalid_grant')
    req = Request('', '', payload=http.payload.URLEncodedFormData({'grant_type': 'password'}))
    resp = Response(400, {}, b'{"error": "invalid_grant"}')
    with pytest.raises(exceptions.GrantCredentialsError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, req, resp)
    assert '2FA' in str(exc_info.value)

    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://www.reddit.com/api/v1/access_token', headers={'Authorization': 'Basic waterfall'})
    resp = Response(401, {}, b'')
    with pytest.raises(exceptions.ClientCredentialsError):
        raise_for_reddit_auth_response_exception(exc, req, resp)

def test_FaultyUserAgent() -> None:
    exc = http.exceptions.StatusCodeException(status_code=429)
    req = Request('', '', headers={'User-Agent': 'xcurlx'})
    resp = Response(429, {}, b'')
    with pytest.raises(exceptions.FaultyUserAgent):
        raise_for_reddit_auth_response_exception(exc, req, resp)

def test_UnsupportedGrantType() -> None:
    exc = auth.exceptions.TokenServerResponseErrorTypes.UnsupportedGrantType(error_name='unsupported_grant_type')
    req = Request('', '', headers={'Content-Type': 'application/json'})
    resp = Response(200, {}, b'')
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.value.arg is not None
