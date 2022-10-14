
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import MutableMapping, Optional, List

import pytest

from redditwarp.auth.token_revocation_client_SYNC import TokenRevocationClient
from redditwarp.http.exceptions import StatusCodeException
from redditwarp.http.requestor_SYNC import Requestor
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import URLEncodedFormData

class MockRequestor(Requestor):
    def __init__(self,
        response_status: int,
        response_headers: MutableMapping[str, str],
        response_data: bytes,
    ) -> None:
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data
        self.history: List[Request] = []

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

def test_revoke_token() -> None:
    requestor = MockRequestor(
        response_status=200,
        response_headers={},
        response_data=b'',
    )
    uri = 'abcdef'
    client_credentials = ('cid', 'cse')
    trc = TokenRevocationClient(
        requestor,
        uri,
        client_credentials,
    )
    trc.revoke_token('a1', 'a2')

    assert len(requestor.history) == 1
    req = requestor.history[0]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, URLEncodedFormData)
    assert req.payload.data == {'token': 'a1', 'token_type_hint': 'a2'}

    trc.revoke_token('b1', '')
    assert len(requestor.history) == 2
    req = requestor.history[1]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, URLEncodedFormData)
    assert req.payload.data == {'token': 'b1'}

def test_revoke_token__exceptions() -> None:
    requestor = MockRequestor(
        response_status=502,
        response_headers={},
        response_data=b'',
    )
    trc = TokenRevocationClient(
        requestor,
        '', ('cid', 'cse'),
    )
    with pytest.raises(StatusCodeException):
        trc.revoke_token('', '')

def test_revoke_access_token() -> None:
    class MyTokenRevocationClient(TokenRevocationClient):
        def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
            assert token == 'abc'
            assert token_type_hint == 'access_token'

    trc = MyTokenRevocationClient(Requestor(), '', ('', ''))
    trc.revoke_access_token('abc')

def test_revoke_refresh_token() -> None:
    class MyTokenRevocationClient(TokenRevocationClient):
        def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> None:
            assert token == 'def'
            assert token_type_hint == 'refresh_token'

    trc = MyTokenRevocationClient(Requestor(), '', ('', ''))
    trc.revoke_refresh_token('def')
