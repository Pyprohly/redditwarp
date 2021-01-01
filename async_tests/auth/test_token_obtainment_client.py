
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, Optional, Any, List

import pytest

from redditwarp.auth.token_obtainment_client_ASYNC import TokenObtainmentClient
from redditwarp.auth.client_credentials import ClientCredentials
from redditwarp.auth.util import basic_auth
from redditwarp.auth.exceptions import (
    ResponseContentError,
    InvalidClient,
    UnrecognizedOAuth2ResponseError,
)
from redditwarp.http.requestor_ASYNC import Requestor
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

    async def send(self, request: Request, *, timeout: float = 0,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

@pytest.mark.asyncio
async def test_fetch_json_dict() -> None:
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
    resp_json = await o.fetch_json_dict()

    assert resp_json == {'a': 100, "some": "text"}
    assert len(requestor.history) == 1
    req = requestor.history[0]
    assert req.verb == 'POST'
    assert req.uri == uri
    assert isinstance(req.payload, FormData)
    assert req.payload.data == {'grant_type': 'epyt_tnarg', 'data1': 'blah'}
    assert req.headers['Authorization'] == basic_auth(client_credentials)

@pytest.mark.asyncio
async def test_fetch_json_dict__exceptions() -> None:
    requestor = MockRequestor(
        response_status=200,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'["hi"]',
    )
    o = TokenObtainmentClient(
        requestor,
        '', ClientCredentials('cid', 'cse'), {},
    )
    with pytest.raises(ResponseContentError):
        await o.fetch_json_dict()

    o.requestor = MockRequestor(
        response_status=599,
        response_headers={},
        response_data=b'{"error": "invalid_client"}',
    )
    with pytest.raises(ResponseContentError):
        await o.fetch_json_dict()

    o.requestor = MockRequestor(
        response_status=599,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "invalid_client"}',
    )
    with pytest.raises(InvalidClient):
        await o.fetch_json_dict()

    o.requestor = MockRequestor(
        response_status=599,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "asdf"}',
    )
    with pytest.raises(UnrecognizedOAuth2ResponseError):
        await o.fetch_json_dict()

    o.requestor = MockRequestor(
        response_status=401,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"message": "Unauthorized", "error": 401}',
    )
    with pytest.raises(UnrecognizedOAuth2ResponseError):
        await o.fetch_json_dict()

@pytest.mark.asyncio
async def test_fetch_token() -> None:
    class MyTokenObtainmentClient(TokenObtainmentClient):
        async def fetch_json_dict(self) -> Mapping[str, Any]:
            return {
                'access_token': 'aoeu',
                'token_type': ';qjk',
                'expires_in': 1234,
                'refresh_token': 'asdf',
                'scope': 'zxcv',
            }

    tk = await MyTokenObtainmentClient(
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
