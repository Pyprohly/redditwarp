
from __future__ import annotations

import pytest

from redditwarp import http
from redditwarp import auth
from redditwarp.http.requisition import Requisition, make_requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.exchange import Exchange
from redditwarp.core.exceptions import raise_for_reddit_auth_response_exception
from redditwarp.core import exceptions


def make_exchange(requisition: Requisition, request: Request, response: Response) -> Exchange:
    return Exchange(
        requisition=requisition,
        request=request,
        response=response,
        history=(),
    )


def test_incorrect_access_token_url() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    xchg = make_exchange(
        Requisition('GET', "https://reddit.com/api/v1/access_token", {}, {}, None),
        Request('', '', {}, b''),
        Response(401, {}, b''),
    )
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, xchg)
    assert exc_info.match('token URL')

def test_no_authorization_header() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    xchg = make_exchange(
        Requisition('GET', "https://www.reddit.com/api/v1/access_token", {}, {}, None),
        Request('', '', {}, b''),
        Response(401, {}, b''),
    )
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, xchg)
    assert exc_info.match('Authorization')

def test_authorization_header_no_basic() -> None:
    exc = http.exceptions.StatusCodeException(status_code=401)
    xchg = make_exchange(
        Requisition('GET', "https://www.reddit.com/api/v1/access_token", {}, {}, None),
        Request('', '', {'Authorization': 'asdf'}, b''),
        Response(401, {}, b''),
    )
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, xchg)
    assert exc_info.match('Basic')

def test_BlacklistedUserAgent() -> None:
    exc = http.exceptions.StatusCodeException(status_code=403)
    xchg = make_exchange(
        Requisition('', '', {}, {}, None),
        Request('', '', {'User-Agent': 'xscrapingx'}, b''),
        Response(403, {}, b'<!doctype html>'),
    )
    with pytest.raises(exceptions.BlacklistedUserAgent):
        raise_for_reddit_auth_response_exception(exc, xchg)

def test_CredentialsError() -> None:
    exc: Exception = auth.exceptions.TokenServerResponseErrorTypes.InvalidGrant(error_name='invalid_grant')
    xchg = make_exchange(
        Requisition('', '', {}, {}, None),
        Request('', '', {}, b''),
        Response(400, {}, b'{"error": "invalid_grant"}'),
    )
    with pytest.raises(exceptions.GrantCredentialsError):
        raise_for_reddit_auth_response_exception(exc, xchg)

    exc = auth.exceptions.TokenServerResponseErrorTypes.InvalidGrant(error_name='invalid_grant')
    xchg = make_exchange(
        make_requisition('', '', data={'grant_type': 'password'}),
        Request('', '', {}, b''),
        Response(400, {}, b'{"error": "invalid_grant"}'),
    )
    with pytest.raises(exceptions.GrantCredentialsError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, xchg)
    assert '2FA' in str(exc_info.value)

    exc = http.exceptions.StatusCodeException(status_code=401)
    xchg = make_exchange(
        make_requisition('GET', "https://www.reddit.com/api/v1/access_token", data={'grant_type': 'password'}),
        Request('', '', {'Authorization': 'Basic waterfall'}, b''),
        Response(401, {}, b''),
    )
    with pytest.raises(exceptions.ClientCredentialsError):
        raise_for_reddit_auth_response_exception(exc, xchg)

def test_FaultyUserAgent() -> None:
    exc = http.exceptions.StatusCodeException(status_code=429)
    xchg = make_exchange(
        Requisition('', '', {}, {}, None),
        Request('', '', {'User-Agent': 'xcurlx'}, b''),
        Response(429, {}, b''),
    )
    with pytest.raises(exceptions.FaultyUserAgent):
        raise_for_reddit_auth_response_exception(exc, xchg)

def test_UnsupportedGrantType() -> None:
    exc = auth.exceptions.TokenServerResponseErrorTypes.UnsupportedGrantType(error_name='unsupported_grant_type')
    xchg = make_exchange(
        Requisition('', '', {}, {}, None),
        Request('', '', {'Content-Type': 'application/json'}, b''),
        Response(200, {}, b''),
    )
    with pytest.raises(exceptions.AuthError) as exc_info:
        raise_for_reddit_auth_response_exception(exc, xchg)
    assert exc_info.value.arg is not None

def test_500_http_error_on_auth_code_reuse() -> None:
    exc = http.exceptions.StatusCodeException(status_code=404)
    xchg = make_exchange(
        make_requisition('', '', data={'grant_type': 'authorization_code'}),
        Request('', '', {}, b''),
        Response(404, {}, b''),
    )
    with pytest.raises(http.exceptions.StatusCodeException) as exc_info:
        raise_for_reddit_auth_response_exception(exc, xchg)
    assert 'expired' in str(exc_info.value)

def test_refresh_token_invalid() -> None:
    exc = http.exceptions.StatusCodeException(status_code=400)
    xchg = make_exchange(
        make_requisition('', '', data={'grant_type': 'refresh_token'}),
        Request('', '', {}, b''),
        Response(200, {}, b''),
    )
    with pytest.raises(http.exceptions.StatusCodeException) as exc_info:
        raise_for_reddit_auth_response_exception(exc, xchg)
    assert 'refresh' in str(exc_info.value)
