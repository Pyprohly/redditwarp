
from __future__ import annotations
from typing import Mapping

import pytest

from redditwarp import exceptions
from redditwarp.http import exceptions as http_exceptions
from redditwarp.client_ASYNC import Client
from redditwarp.core.http_client_ASYNC import HTTPClient
from redditwarp.http.handler_ASYNC import Handler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.requisition import Requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response


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


@pytest.mark.asyncio
async def test_request() -> None:
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"some": "data"}')
    client = Client.from_http(http)
    data = await client.request('', '')
    assert data == {"some": "data"}

@pytest.mark.asyncio
async def test_zero_data() -> None:
    # Test None is returned on zero data even when Content-Type is 'application/json'.
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'')
    client = Client.from_http(http)
    data = await client.request('', '')
    assert data is None

@pytest.mark.asyncio
async def test_last_value() -> None:
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"a": 1}')
    client = Client.from_http(http)
    await client.request('', '')
    assert client.last_value == {'a': 1}
    http.response_data = b''
    await client.request('', '')
    assert client.last_value is None

class TestRequestExceptions:
    @pytest.mark.asyncio
    async def test_json_decode_failed_and_status_code_exception(self) -> None:
        http = MyHTTPClient(414, {'Content-Type': 'text/plain'}, b'Error: URI Too Long')
        client = Client.from_http(http)
        with pytest.raises(http_exceptions.StatusCodeException):
            await client.request('', '')

    @pytest.mark.asyncio
    async def test_json_decode_succeeded_but_status_code_exception(self) -> None:
        http = MyHTTPClient(404, {'Content-Type': 'application/json; charset=UTF-8'}, b'{"message": "Not Found", "error": 404}')
        client = Client.from_http(http)
        with pytest.raises(http_exceptions.StatusCodeException):
            await client.request('', '')

    @pytest.mark.asyncio
    async def test_no_content_type_in_response(self) -> None:
        http = MyHTTPClient(200, {}, b'{"some": "data"}')
        client = Client.from_http(http)
        with pytest.raises(ValueError):
            await client.request('', '')

    @pytest.mark.asyncio
    async def test_non_json_response(self) -> None:
        http = MyHTTPClient(200, {'Content-Type': 'text/html'}, b'<!DOCTYPE html>')
        client = Client.from_http(http)
        with pytest.raises(ValueError):
            await client.request('', '')

        http = MyHTTPClient(403, {'Content-Type': 'text/html'}, b'>user agent required</')
        client = Client.from_http(http)
        with pytest.raises(exceptions.UserAgentRequired) as exc_info:
            await client.request('', '')
        assert exc_info.value.arg is not None

        http = MyHTTPClient(500, {'Content-Type': 'text/html'}, b'>Our CDN was unable to reach our servers</')
        client = Client.from_http(http)
        with pytest.raises(http_exceptions.StatusCodeException) as exc_info1:
            await client.request('', '')
        assert isinstance(arg := exc_info1.value.arg, str) and 'CDN' in arg

    @pytest.mark.asyncio
    async def test_variant1_reddit_error(self) -> None:
        b = b'''\
{
    "explanation": "Please log in to do that.",
    "message": "Forbidden",
    "reason": "USER_REQUIRED"
}
'''
        http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b)
        client = Client.from_http(http)
        with pytest.raises(exceptions.RedditError) as exc_info:
            await client.request('', '')
        exc = exc_info.value
        assert exc.label == "USER_REQUIRED"
        assert exc.explanation == "Please log in to do that."
        assert exc.field == ""

        b = b'''\
{
    "fields": ["title"],
    "explanation": "this is too long (max: 50)",
    "message": "Bad Request",
    "reason": "TOO_LONG"
}
'''
        http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b)
        client = Client.from_http(http)
        with pytest.raises(exceptions.RedditError) as exc_info:
            await client.request('', '')
        exc = exc_info.value
        assert exc.label == "TOO_LONG"
        assert exc.explanation == "this is too long (max: 50)"
        assert exc.field == "title"

    @pytest.mark.asyncio
    async def test_variant2_reddit_error(self) -> None:
        b = b'''\
{
    "json": {
        "errors": [
            ["NO_TEXT", "we need something here", "title"],
            ["BAD_URL", "you should check that url", "url"]
        ]
    }
}
'''
        http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b)
        client = Client.from_http(http)
        with pytest.raises(exceptions.RedditError) as exc_info:
            await client.request('', '')
        exc = exc_info.value
        assert exc.label == 'NO_TEXT'
        assert exc.explanation == 'we need something here'
        assert exc.field == 'title'
