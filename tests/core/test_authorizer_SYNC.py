
from __future__ import annotations
from typing import Optional, MutableSequence

import pytest

from redditwarp.core.authorizer_SYNC import Authorizer, Authorized
from redditwarp.auth.token import Token
from redditwarp.auth.token_obtainment_client_SYNC import TokenObtainmentClient
from redditwarp.auth.exceptions import UnknownTokenType
from redditwarp.http.requestor_SYNC import Requestor
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.session_base_SYNC import SessionBase
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

    def fetch_token(self) -> Token:
        return self.my_token

class MyAuthorizer(Authorizer):
    def time(self) -> float:
        return 10


class TestAuthorizer:
    def test_renew_token(self) -> None:
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
        o.renewal_skew = 40

        o.renewal_time = 9999
        o.expires_in_fallback = None
        o.renew_token()
        assert o.get_token() is my_token
        assert o.renewal_time is None

        o.renewal_time = 9999
        token_client.my_token = get_token(expires_in=234)
        o.expires_in_fallback = None
        o.renew_token()
        expires_in = token_client.my_token.expires_in
        assert expires_in is not None
        assert o.renewal_time == int(o.time()) + expires_in - o.renewal_skew

        o.renewal_time = 9999
        token_client.my_token = get_token(expires_in=None)
        o.expires_in_fallback = 125
        o.renew_token()
        assert o.renewal_time == int(o.time()) + o.expires_in_fallback - o.renewal_skew

    def test_renew_token__no_token_client(self) -> None:
        with pytest.raises(RuntimeError):
            Authorizer(token=None, token_client=None).renew_token()

    def test_renew_token__unknown_token_Type(self) -> None:
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


class MockSession(SessionBase):
    def __init__(self,
        responses: MutableSequence[Response],
    ) -> None:
        super().__init__()
        self.responses = responses

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        return self.responses.pop(0)

class TestAuthorized:
    dummy_request = Request('', '', params={}, headers={}, payload=None)

    def test_ResourceServerResponseError(self) -> None:
        session = MockSession([
            Response(403, {'WWW-Authenticate': 'Bearer realm="reddit", error="insufficient_scope"'}, b'{"message": "Forbidden", "error": 403}'),
        ])
        token_client = MyTokenObtainmentClient(Token('token'))
        authorizer = Authorizer(
            token=None,
            token_client=token_client,
        )
        requestor = Authorized(session, authorizer)
        with pytest.raises(auth.exceptions.ResourceServerResponseErrorTypes.InsufficientScope):
            requestor.send(self.dummy_request)

    def test_invalid_token_to_ResourceServerResponseError(self) -> None:
        session = MockSession([
            Response(401, {'WWW-Authenticate': 'Bearer realm="reddit", error="invalid_token"'}, b''),
            Response(403, {'WWW-Authenticate': 'Bearer realm="reddit", error="insufficient_scope"'}, b'{"message": "Forbidden", "error": 403}'),
        ])
        token_client = MyTokenObtainmentClient(Token('token'))
        authorizer = Authorizer(
            token=None,
            token_client=token_client,
        )
        requestor = Authorized(session, authorizer)
        with pytest.raises(auth.exceptions.ResourceServerResponseErrorTypes.InsufficientScope):
            requestor.send(self.dummy_request)

    def test_token_gets_changed_for_second_request_after_an_invalid_token_response(self) -> None:
        session = MockSession([
            Response(401, {'WWW-Authenticate': 'Bearer realm="reddit", error="invalid_token"'}, b''),
            Response(200, {}, b''),
        ])
        token_client = MyTokenObtainmentClient(Token('token_two'))
        authorizer = Authorizer(
            token=Token('token_one'),
            token_client=token_client,
        )
        requestor = Authorized(session, authorizer)
        req = self.dummy_request
        requestor.send(req)
        assert req.headers[authorizer.authorization_header_name].partition(' ')[-1] == 'token_two'
