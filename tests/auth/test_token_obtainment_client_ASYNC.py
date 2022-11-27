
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, Any

import pytest

from redditwarp.auth.token_obtainment_client_ASYNC import TokenObtainmentClient
from redditwarp.auth.utils import basic_auth
from redditwarp.auth.exceptions import (
    TokenServerResponseErrorTypes,
    UnrecognizedTokenServerResponseError,
)
from redditwarp.http import exceptions as http_exceptions
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
    DUMMY_REQUEST = Request('', '', {})

    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__(Handler())
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    async def send(self, p: SendParams) -> Exchange:
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

    async def send(self, p: SendParams) -> Exchange:
        self.history.append(p.requisition)
        return await super().send(p)


@pytest.mark.asyncio
async def test_fetch_data() -> None:
    http = RecordingHTTPClient(
        response_status=200,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"a":100, "some": "text"}',
    )
    url = 'abcdef'
    client_credentials = ('cid', 'cse')
    grant = {'grant_type': 'epyt_tnarg', 'data1': 'blah', 'data2': ''}
    toc = TokenObtainmentClient(
        http,
        url,
        client_credentials,
        grant,
    )
    resp_json = await toc.fetch_data()

    assert resp_json == {'a': 100, "some": "text"}
    assert len(http.history) == 1
    req = http.history[0]
    assert req.verb == 'POST'
    assert req.url == url
    assert isinstance(req.payload, URLEncodedFormData)
    assert req.payload.data == {'grant_type': 'epyt_tnarg', 'data1': 'blah', 'data2': ''}
    assert req.headers['Authorization'] == basic_auth(*client_credentials)

@pytest.mark.asyncio
async def test_fetch_json_dict__exceptions() -> None:
    def new_token_obtainment_client(http: HTTPClient) -> TokenObtainmentClient:
        return TokenObtainmentClient(http, '', ('', ''), {})

    http = MyHTTPClient(
        response_status=599,
        response_headers={},
        response_data=b'{"error": "invalid_client"}',
    )
    toc = new_token_obtainment_client(http)
    with pytest.raises(http_exceptions.StatusCodeException):
        await toc.fetch_data()

    http = MyHTTPClient(
        response_status=599,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "invalid_client"}',
    )
    toc = new_token_obtainment_client(http)
    with pytest.raises(TokenServerResponseErrorTypes.InvalidClient):
        await toc.fetch_data()

    http = MyHTTPClient(
        response_status=599,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"error": "asdf"}',
    )
    toc = new_token_obtainment_client(http)
    with pytest.raises(UnrecognizedTokenServerResponseError):
        await toc.fetch_data()

    http = MyHTTPClient(
        response_status=401,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"message": "Unauthorized", "error": 401}',
    )
    toc = new_token_obtainment_client(http)
    with pytest.raises(UnrecognizedTokenServerResponseError):
        await toc.fetch_data()

@pytest.mark.asyncio
async def test_fetch_token() -> None:
    class MyTokenObtainmentClient(TokenObtainmentClient):
        async def fetch_data(self) -> Mapping[str, Any]:
            return {
                'access_token': 'aoeu',
                'token_type': ';qjk',
                'expires_in': 1234,
                'refresh_token': 'asdf',
                'scope': 'zxcv',
            }

    tk = await MyTokenObtainmentClient(HTTPClient(Handler()), '', ('', ''), {}).fetch_token()
    assert tk.access_token == 'aoeu'
    assert tk.token_type == ';qjk'
    assert tk.expires_in == 1234
    assert tk.refresh_token == 'asdf'
    assert tk.scope == 'zxcv'
