
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, Optional, Any

import pytest

from redditwarp.auth.token_obtainment_client_sync import TokenObtainmentClient
from redditwarp.auth.client_credentials import ClientCredentials
from redditwarp.auth.token import ResponseToken
from redditwarp.auth.util import basic_auth
from redditwarp.auth.exceptions import (
    ResponseContentError,
    InvalidClient,
    HTTPStatusError,
    UnrecognizedOAuth2ResponseError,
)
from redditwarp.http.requestor import Requestor
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
        self.history = []

    def request(self, request: Request, *, timeout: Optional[float] = None,
            aux_info: Optional[Mapping] = None) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

def test_fetch_json_dict():
    requestor = MockRequestor(
        response_status=200,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"a":100, "some": "text"}',
    )
    uri = 'abcdef'
    client_credentials = ClientCredentials('cid', 'cse')
    grant = {'grant_type': 'epyt_tnarg', 'data1': 'blah', 'data2': '', 'data3': None}
    o = TokenObtainmentClient(
        requestor,
        uri,
        client_credentials,
        grant,
    )
    resp_json = o.fetch_json_dict()

    assert resp_json == {'a': 100, "some": "text"}
    assert len(requestor.history) == 1
    req = requestor.history[0]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, FormData)
    assert req.payload.data == {'grant_type': 'epyt_tnarg', 'data1': 'blah'}
    assert req.headers['Authorization'] == basic_auth(client_credentials)

def test_fetch_json_dict__exceptions():
    requestor = MockRequestor(
        response_status=502,
        response_headers={},
        response_data=b'{"error": "invalid_client"}',
    )
    o = TokenObtainmentClient(
        requestor,
        '', ClientCredentials('cid', 'cse'), {},
    )
    with pytest.raises(ResponseContentError):
        o.fetch_json_dict()

    o.requestor = MockRequestor(
        response_status=502,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "invalid_client"}',
    )
    with pytest.raises(InvalidClient):
        o.fetch_json_dict()

    o.requestor = MockRequestor(
        response_status=502,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "bogus"}',
    )
    with pytest.raises(HTTPStatusError):
        o.fetch_json_dict()

    o.requestor = MockRequestor(
        response_status=200,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "bogus"}',
    )
    with pytest.raises(UnrecognizedOAuth2ResponseError):
        o.fetch_json_dict()

def test_fetch_token():
    class MyTokenObtainmentClient(TokenObtainmentClient):
        def fetch_json_dict(self) -> Mapping[str, Any]:
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
        ClientCredentials('', ''),
        {},
    ).fetch_token()
    assert tk.access_token == 'aoeu'
    assert tk.token_type == ';qjk'
    assert tk.expires_in == 1234
    assert tk.refresh_token == 'asdf'
    assert tk.scope == 'zxcv'