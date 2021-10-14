
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, MutableMapping, Any, List

import pytest

from redditwarp.auth.token_obtainment_client_SYNC import TokenObtainmentClient
from redditwarp.auth.util import basic_auth
from redditwarp.auth.exceptions import (
    TokenServerResponseErrorTypes,
    UnrecognizedTokenServerResponseError,
)
from redditwarp import http
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

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

def test_fetch_json_dict() -> None:
    requestor = MockRequestor(
        response_status=200,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"a":100, "some": "text"}',
    )
    uri = 'abcdef'
    client_credentials = ('cid', 'cse')
    grant = {'grant_type': 'epyt_tnarg', 'data1': 'blah', 'data2': ''}
    toc = TokenObtainmentClient(
        requestor,
        uri,
        client_credentials,
        grant,
    )
    resp_json = toc.fetch_data()

    assert resp_json == {'a': 100, "some": "text"}
    assert len(requestor.history) == 1
    req = requestor.history[0]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, URLEncodedFormData)
    assert req.payload.data == {'grant_type': 'epyt_tnarg', 'data1': 'blah', 'data2': ''}
    assert req.headers['Authorization'] == basic_auth(*client_credentials)

def test_fetch_json_dict__exceptions() -> None:
    toc = TokenObtainmentClient(
        Requestor(),
        '', ('cid', 'cse'), {},
    )

    toc.requestor = MockRequestor(
        response_status=599,
        response_headers={},
        response_data=b'{"error": "invalid_client"}',
    )
    with pytest.raises(http.exceptions.StatusCodeException):
        toc.fetch_data()

    toc.requestor = MockRequestor(
        response_status=599,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "invalid_client"}',
    )
    with pytest.raises(TokenServerResponseErrorTypes.InvalidClient):
        toc.fetch_data()

    toc.requestor = MockRequestor(
        response_status=599,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "asdf"}',
    )
    with pytest.raises(UnrecognizedTokenServerResponseError):
        toc.fetch_data()

    toc.requestor = MockRequestor(
        response_status=401,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"message": "Unauthorized", "error": 401}',
    )
    with pytest.raises(UnrecognizedTokenServerResponseError):
        toc.fetch_data()

def test_fetch_token() -> None:
    class MyTokenObtainmentClient(TokenObtainmentClient):
        def fetch_data(self) -> Mapping[str, Any]:
            return {
                'access_token': 'aoeu',
                'token_type': ';qjk',
                'expires_in': 1234,
                'refresh_token': 'asdf',
                'scope': 'zxcv',
            }

    tk = MyTokenObtainmentClient(
        Requestor(),
        '',
        ('', ''),
        {},
    ).fetch_token()
    assert tk.access_token == 'aoeu'
    assert tk.token_type == ';qjk'
    assert tk.expires_in == 1234
    assert tk.refresh_token == 'asdf'
    assert tk.scope == 'zxcv'
