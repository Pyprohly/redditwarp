
from __future__ import annotations
from typing import Optional, MutableSequence, Sequence

import pytest

from redditwarp.core.authorizer_ASYNC import Authorizer, Authorized
from redditwarp.auth.token import Token
from redditwarp.auth.token_obtainment_client_ASYNC import TokenObtainmentClient
from redditwarp.auth.exceptions import UnknownTokenType
from redditwarp.http.http_client_ASYNC import HTTPClient
from redditwarp.http.handler_ASYNC import Handler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp import auth

class MyTokenObtainmentClient(TokenObtainmentClient):
    def __init__(self, my_token: Token) -> None:
        super().__init__(HTTPClient(Handler()), '', ('', ''), {})
        self.my_token = my_token

    async def fetch_token(self) -> Token:
        return self.my_token

class MyAuthorizer(Authorizer):
    def time(self) -> float:
        return 10


class TestAuthorizer:
    @pytest.mark.asyncio
    async def test_renew_token(self) -> None:
        def new_token(expires_in: Optional[int]) -> Token:
            return Token(
                access_token='a',
                token_type='bearer',
                expires_in=expires_in,
                refresh_token='c',
                scope='d',
            )

        my_token = new_token(expires_in=None)
        token_client = MyTokenObtainmentClient(my_token)
        o = MyAuthorizer(
            token_client=token_client,
            token=None,
        )
        o.renewal_skew = 40

        o.renewal_time = 9999
        o.expires_in_fallback = None
        await o.renew_token()
        assert o.fetch_token() is my_token
        assert o.renewal_time is None

        o.renewal_time = 9999
        token_client.my_token = new_token(expires_in=234)
        o.expires_in_fallback = None
        await o.renew_token()
        expires_in = token_client.my_token.expires_in
        assert expires_in is not None
        assert o.renewal_time == int(o.time()) + expires_in - o.renewal_skew

        o.renewal_time = 9999
        token_client.my_token = new_token(expires_in=None)
        o.expires_in_fallback = 125
        await o.renew_token()
        assert o.renewal_time == int(o.time()) + o.expires_in_fallback - o.renewal_skew

    @pytest.mark.asyncio
    async def test_renew_token__no_token_client(self) -> None:
        with pytest.raises(RuntimeError):
            await Authorizer(token_client=None, token=None).renew_token()

    @pytest.mark.asyncio
    async def test_renew_token__unknown_token_Type(self) -> None:
        def new_token(token_type: str) -> Token:
            return Token(
                access_token='a',
                token_type=token_type,
                expires_in=1,
                refresh_token='c',
                scope='d',
            )

        token_client = MyTokenObtainmentClient(new_token('bearer'))
        o = Authorizer(token_client=token_client, token=None)
        await o.renew_token()

        token_client.my_token = new_token('Bearer')
        await o.renew_token()

        token_client.my_token = new_token('bEaReR')
        await o.renew_token()

        token_client.my_token = new_token('bear')
        with pytest.raises(UnknownTokenType):
            await o.renew_token()


class ReplayingHandler(Handler):
    DUMMY_REQUEST = Request('', '', {}, b'')

    def __init__(self, responses: Sequence[Response]) -> None:
        super().__init__()
        self.responses: MutableSequence[Response] = list(responses)

    async def _send(self, p: SendParams) -> Exchange:
        resp = self.responses.pop(0)
        return Exchange(
            requisition=p.requisition,
            request=self.DUMMY_REQUEST,
            response=resp,
            history=(),
        )


class TestAuthorized:
    @pytest.mark.asyncio
    async def test_ResourceServerResponseError(self) -> None:
        handler: Handler = ReplayingHandler([
            Response(403, {'WWW-Authenticate': 'Bearer realm="reddit", error="insufficient_scope"'}, b'{"message": "Forbidden", "error": 403}'),
        ])
        token_client = MyTokenObtainmentClient(Token('token'))
        authorizer = Authorizer(
            token_client=token_client,
            token=None,
        )
        handler = Authorized(handler, authorizer)
        with pytest.raises(auth.exceptions.ResourceServerResponseErrorTypes.InsufficientScope):
            await HTTPClient(handler).request('', '')

    @pytest.mark.asyncio
    async def test_invalid_token_to_ResourceServerResponseError(self) -> None:
        handler: Handler = ReplayingHandler([
            Response(401, {'WWW-Authenticate': 'Bearer realm="reddit", error="invalid_token"'}, b''),
            Response(403, {'WWW-Authenticate': 'Bearer realm="reddit", error="insufficient_scope"'}, b'{"message": "Forbidden", "error": 403}'),
        ])
        token_client = MyTokenObtainmentClient(Token('token'))
        authorizer = Authorizer(
            token_client=token_client,
            token=None,
        )
        handler = Authorized(handler, authorizer)
        with pytest.raises(auth.exceptions.ResourceServerResponseErrorTypes.InsufficientScope):
            await HTTPClient(handler).request('', '')

    @pytest.mark.asyncio
    async def test_token_gets_changed_for_second_request_after_an_invalid_token_response(self) -> None:
        handler: Handler = ReplayingHandler([
            Response(401, {'WWW-Authenticate': 'Bearer realm="reddit", error="invalid_token"'}, b''),
            Response(200, {}, b''),
        ])
        token_client = MyTokenObtainmentClient(Token('token_two'))
        authorizer = Authorizer(
            token_client=token_client,
            token=Token('token_one'),
        )
        handler = Authorized(handler, authorizer)
        reqi = HTTPClient.make_requisition('', '')
        await HTTPClient(handler).submit(reqi)
        assert reqi.headers[authorizer.authorization_header_name].partition(' ')[-1] == 'token_two'
