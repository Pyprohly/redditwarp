
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, Optional, List

import pytest  # type: ignore[import]

from redditwarp.auth.token_revocation_client_sync import TokenRevocationClient
from redditwarp.auth.client_credentials import ClientCredentials
from redditwarp.auth.exceptions import HTTPStatusError
from redditwarp.http.requestor_sync import Requestor
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import FormData

class MockRequestor(Requestor):
    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data
        self.history: List[Request] = []

    def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

def test_revoke_token() -> None:
    requestor = MockRequestor(
        response_status=200,
        response_headers={},
        response_data=b'',
    )
    uri = 'abcdef'
    client_credentials = ClientCredentials('cid', 'cse')
    o = TokenRevocationClient(
        requestor,
        uri,
        client_credentials,
    )
    o.revoke_token('a1', 'a2')

    assert len(requestor.history) == 1
    req = requestor.history[0]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, FormData)
    assert req.payload.data == {'token': 'a1', 'token_type_hint': 'a2'}

    o.revoke_token('b1', '')
    assert len(requestor.history) == 2
    req = requestor.history[1]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, FormData)
    assert req.payload.data == {'token': 'b1'}

    o.revoke_token('c1', None)
    assert len(requestor.history) == 3
    req = requestor.history[2]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, FormData)
    assert req.payload.data == {'token': 'c1'}

def test_revoke_token__exceptions() -> None:
    requestor = MockRequestor(
        response_status=502,
        response_headers={},
        response_data=b'',
    )
    o = TokenRevocationClient(
        requestor,
        '', ClientCredentials('cid', 'cse'),
    )
    with pytest.raises(HTTPStatusError):
        o.revoke_token('', '')

def test_revoke_access_token() -> None:
    class MyTokenRevocationClient(TokenRevocationClient):
        def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
            assert token == 'abc'
            assert token_type_hint == 'access_token'

    o = MyTokenRevocationClient(Requestor(), '', ClientCredentials('', ''))
    o.revoke_access_token('abc')

def test_revoke_refresh_token() -> None:
    class MyTokenRevocationClient(TokenRevocationClient):
        def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
            assert token == 'def'
            assert token_type_hint == 'refresh_token'

    o = MyTokenRevocationClient(Requestor(), '', ClientCredentials('', ''))
    o.revoke_refresh_token('def')
