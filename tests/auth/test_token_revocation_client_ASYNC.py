
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, Optional

import pytest

from redditwarp.auth.token_revocation_client_ASYNC import TokenRevocationClient
from redditwarp.http.exceptions import StatusCodeException
from redditwarp.http.http_client_ASYNC import HTTPClient
from redditwarp.http.handler_ASYNC import Handler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.requisition import Requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import URLEncodedFormData


class MyHTTPClient(HTTPClient):
    DUMMY_REQUISITION = Requisition('', '', {}, {}, None)
    DUMMY_REQUEST = Request('', '', {}, b'')

    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__(Handler())
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    async def _send(self, p: SendParams) -> Exchange:
        resp = Response(self.response_status, self.response_headers, self.response_data)
        return Exchange(
            requisition=self.DUMMY_REQUISITION,
            request=self.DUMMY_REQUEST,
            response=resp,
            history=(),
        )

class RecordingHTTPClient(MyHTTPClient):
    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__(response_status, response_headers, response_data)
        self.history: list[Requisition] = []

    async def _send(self, p: SendParams) -> Exchange:
        self.history.append(p.requisition)
        return await super()._send(p)


@pytest.mark.asyncio
async def test_revoke_token() -> None:
    http = RecordingHTTPClient(
        response_status=200,
        response_headers={},
        response_data=b'',
    )
    url = 'abcdef'
    client_credentials = ('cid', 'cse')
    trc = TokenRevocationClient(
        http,
        url,
        client_credentials,
    )
    await trc.revoke_token('a1', 'a2')

    assert len(http.history) == 1
    req = http.history[0]
    assert req.verb == 'POST'
    assert req.url == url
    assert isinstance(req.payload, URLEncodedFormData)
    assert req.payload.data == {'token': 'a1', 'token_type_hint': 'a2'}

    await trc.revoke_token('b1', '')
    assert len(http.history) == 2
    req = http.history[1]
    assert req.verb == 'POST'
    assert req.url == url
    assert isinstance(req.payload, URLEncodedFormData)
    assert req.payload.data == {'token': 'b1'}

@pytest.mark.asyncio
async def test_revoke_token__exceptions() -> None:
    http = MyHTTPClient(
        response_status=502,
        response_headers={},
        response_data=b'',
    )
    trc = TokenRevocationClient(http, '', ('cid', 'cse'))
    with pytest.raises(StatusCodeException):
        await trc.revoke_token('', '')

@pytest.mark.asyncio
async def test_revoke_access_token() -> None:
    class MyTokenRevocationClient(TokenRevocationClient):
        async def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
            assert token == 'abc'
            assert token_type_hint == 'access_token'

    trc = MyTokenRevocationClient(HTTPClient(Handler()), '', ('', ''))
    await trc.revoke_access_token('abc')

@pytest.mark.asyncio
async def test_revoke_refresh_token() -> None:
    class MyTokenRevocationClient(TokenRevocationClient):
        async def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
            assert token == 'def'
            assert token_type_hint == 'refresh_token'

    trc = MyTokenRevocationClient(HTTPClient(Handler()), '', ('', ''))
    await trc.revoke_refresh_token('def')
