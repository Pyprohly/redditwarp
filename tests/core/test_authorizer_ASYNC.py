
from __future__ import annotations
from typing import Optional, MutableSequence

import pytest

from redditwarp.core.authorizer_ASYNC import Authorizer, Authorized
from redditwarp.auth.token import Token
from redditwarp.auth.token_obtainment_client_ASYNC import TokenObtainmentClient
from redditwarp.core.exceptions import UnknownTokenType
from redditwarp.http.requestor_ASYNC import Requestor
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.session_base_ASYNC import SessionBase
from redditwarp import auth

class MyTokenObtainmentClient(TokenObtainmentClient):
    def __init__(self, my_token: Token) -> None:
        super().__init__(
            requestor=Requestor(),
            uri='',
            client_credentials=('', ''),
            grant={},
        )
        self.my_token = my_token

    async def fetch_token(self) -> Token:
        return self.my_token

class MyAuthorizer(Authorizer):
    def current_time(self) -> float:
        return 10


class TestAuthorizer:
    @pytest.mark.asyncio
    async def test_renew_token(self) -> None:
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
        await o.renew_token()
        assert o.token is my_token
        assert o.expiry_time is None

        o.expiry_time = 9999
        token_client.my_token = get_token(expires_in=234)
        o.expires_in_fallback = None
        await o.renew_token()
        expires_in = token_client.my_token.expires_in
        assert expires_in is not None
        assert o.expiry_time == int(o.current_time()) + expires_in - o.expiry_skew

        o.expiry_time = 9999
        token_client.my_token = get_token(expires_in=None)
        o.expires_in_fallback = 125
        await o.renew_token()
        assert o.expiry_time == int(o.current_time()) + o.expires_in_fallback - o.expiry_skew

    @pytest.mark.asyncio
    async def test_renew_token__no_token_client(self) -> None:
        with pytest.raises(RuntimeError):
            await Authorizer(token=None, token_client=None).renew_token()

    @pytest.mark.asyncio
    async def test_renew_token__unknown_token_Type(self) -> None:
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
        await o.renew_token()

        token_client.my_token = get_token('Bearer')
        await o.renew_token()

        token_client.my_token = get_token('bEaReR')
        await o.renew_token()

        token_client.my_token = get_token('bear')
        with pytest.raises(UnknownTokenType):
            await o.renew_token()


class MockSession(SessionBase):
    def __init__(self,
        responses: MutableSequence[Response],
    ) -> None:
        super().__init__()
        self.responses = responses

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        return self.responses.pop(0)

class TestAuthorized:
    @pytest.mark.asyncio
    async def test_ResourceServerResponseError(self) -> None:
        session = MockSession([
            Response(401, {'WWW-Authenticate': 'Bearer realm="reddit", error="invalid_token"'}, b''),
            Response(403, {'WWW-Authenticate': 'Bearer realm="reddit", error="insufficient_scope"'}, b'{"message": "Forbidden", "error": 403}'),
        ])
        token_client = MyTokenObtainmentClient(Token('token'))
        authorizer = MyAuthorizer(
            token=None,
            token_client=token_client,
        )
        requestor = Authorized(session, authorizer)
        with pytest.raises(auth.exceptions.ResourceServerResponseErrorTypes.InsufficientScope):
            await requestor.send(Request('', ''))
