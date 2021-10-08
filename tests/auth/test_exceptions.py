
from __future__ import annotations

import pytest

from redditwarp import http
from redditwarp import auth
from redditwarp import core
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.core.exceptions import handle_reddit_auth_response_exception

def test_UnidentifiedResponseContentError() -> None:
    exc = ValueError()
    req = Request('', '')
    resp = Response(999, {}, b'')
    with pytest.raises(core.exceptions.UnidentifiedResponseContentError):
        handle_reddit_auth_response_exception(exc, req, resp)

def test_HTMLDocumentResponseContentError() -> None:
    exc = ValueError()
    req = Request('', '')
    resp = Response(999, {'Content-Type': 'text/html'}, b'')
    with pytest.raises(core.exceptions.HTMLDocumentResponseContentError):
        handle_reddit_auth_response_exception(exc, req, resp)

    exc = ValueError()
    req = Request('', '')
    resp = Response(999, {'Content-Type': 'text/html'}, b'Our CDN was unable to reach our servers')
    with pytest.raises(core.exceptions.HTMLDocumentResponseContentError) as exc_info:
        handle_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.value.arg is not None

def test_BlacklistedUserAgent() -> None:
    exc = ValueError()
    req = Request('', '', headers={'User-Agent': 'xscrapingx'})
    resp = Response(403, {}, b'<!doctype html>')
    with pytest.raises(core.exceptions.BlacklistedUserAgent):
        handle_reddit_auth_response_exception(exc, req, resp)

def test_incorrect_access_token_url() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://reddit.com/api/v1/access_token')
    resp = Response(401, {}, b'')
    with pytest.raises(http.exceptions.StatusCodeException) as exc_info:
        handle_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.match('token URL')

def test_no_authorization_header() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://www.reddit.com/api/v1/access_token')
    resp = Response(401, {}, b'')
    with pytest.raises(http.exceptions.StatusCodeException) as exc_info:
        handle_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.match('Authorization')

def test_authorization_header_no_basic() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://www.reddit.com/api/v1/access_token', headers={'Authorization': 'asdf'})
    resp = Response(401, {}, b'')
    with pytest.raises(http.exceptions.StatusCodeException) as exc_info:
        handle_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.match('Basic')

def test_CredentialsError() -> None:
    exc: Exception = auth.exceptions.TokenServerResponseErrorTypes.InvalidGrant(error_name='invalid_grant')
    req = Request('', '')
    resp = Response(400, {}, b'{"error": "invalid_grant"}')
    with pytest.raises(core.exceptions.GrantCredentialsError):
        handle_reddit_auth_response_exception(exc, req, resp)

    exc = http.exceptions.StatusCodeException(status_code=401)
    req = Request('GET', 'https://www.reddit.com/api/v1/access_token', headers={'Authorization': 'Basic waterfall'})
    resp = Response(401, {}, b'')
    with pytest.raises(core.exceptions.ClientCredentialsError):
        handle_reddit_auth_response_exception(exc, req, resp)

def test_FaultyUserAgent() -> None:
    exc = http.exceptions.StatusCodeException(status_code=429)
    req = Request('', '', headers={'User-Agent': 'xcurlx'})
    resp = Response(429, {}, b'')
    with pytest.raises(core.exceptions.FaultyUserAgent):
        handle_reddit_auth_response_exception(exc, req, resp)

def test_UnsupportedGrantType() -> None:
    exc = auth.exceptions.TokenServerResponseErrorTypes.UnsupportedGrantType(error_name='unsupported_grant_type')
    req = Request('', '', headers={'Content-Type': 'application/json'})
    resp = Response(200, {}, b'')
    with pytest.raises(auth.exceptions.TokenServerResponseErrorTypes.UnsupportedGrantType) as exc_info:
        handle_reddit_auth_response_exception(exc, req, resp)
    assert exc_info.value.arg is not None
