
from __future__ import annotations
from typing import Optional

import pytest

from redditwarp.core.authorizer_SYNC import Authorizer
from redditwarp.auth.token import Token
from redditwarp.auth.token_obtainment_client_SYNC import TokenObtainmentClient
from redditwarp.core.exceptions import UnknownTokenType
from redditwarp.http.requestor_SYNC import Requestor

class MyTokenObtainmentClient(TokenObtainmentClient):
    def __init__(self, my_token: Token) -> None:
        super().__init__(
            requestor=Requestor(),
            uri='',
            client_credentials=('', ''),
            grant={},
        )
        self.my_token = my_token

    def fetch_token(self) -> Token:
        return self.my_token

class MyAuthorizer(Authorizer):
    def current_time(self) -> float:
        return 10


def test_renew_token() -> None:
    def get_token(expires_in: Optional[int]) -> Token:
        return Token(
            access_token='a',
            token_type='bearer',
            expires_in=expires_in,
            refresh_token='c',
            scope='d',
        )

    my_token = get_token(expires_in=None)
    token_client = MyTokenObtainmentClient(my_token)
    o = MyAuthorizer(
        token=None,
        token_client=token_client,
    )
    o.expiry_skew = 40

    o.expiry_time = 9999
    o.expires_in_fallback = None
    o.renew_token()
    assert o.token is my_token
    assert o.expiry_time is None

    o.expiry_time = 9999
    token_client.my_token = get_token(expires_in=234)
    o.expires_in_fallback = None
    o.renew_token()
    assert o.expiry_time == int(o.current_time()) + token_client.my_token.expires_in - o.expiry_skew

    o.expiry_time = 9999
    token_client.my_token = get_token(expires_in=None)
    o.expires_in_fallback = 125
    o.renew_token()
    assert o.expiry_time == int(o.current_time()) + o.expires_in_fallback - o.expiry_skew

def test_renew_token__no_token_client_exception() -> None:
    with pytest.raises(RuntimeError):
        Authorizer(token=None, token_client=None).renew_token()

def test_renew_token__unknown_token_Type() -> None:
    def get_token(token_type: str) -> Token:
        return Token(
            access_token='a',
            token_type=token_type,
            expires_in=1,
            refresh_token='c',
            scope='d',
        )

    token_client = MyTokenObtainmentClient(get_token('bearer'))
    o = Authorizer(token=None, token_client=token_client)
    o.renew_token()

    token_client.my_token = get_token('Bearer')
    o.renew_token()

    token_client.my_token = get_token('bEaReR')
    o.renew_token()

    token_client.my_token = get_token('bear')
    with pytest.raises(UnknownTokenType):
        o.renew_token()
