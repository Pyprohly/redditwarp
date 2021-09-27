
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping
if TYPE_CHECKING:
    from redditwarp.http.request import Request

import pytest

from redditwarp import exceptions
from redditwarp.http import exceptions as http_exceptions
from redditwarp.client_ASYNC import Client
from redditwarp.core.reddit_http_client_ASYNC import RedditHTTPClient
from redditwarp.http.session_base_ASYNC import SessionBase
from redditwarp.http.response import Response

class MySession(SessionBase):
    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        raise Exception

class MyHTTPClient(RedditHTTPClient):
    SESSION = MySession()

    def __init__(self,
        response_status: int,
        response_headers: MutableMapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__(session=self.SESSION)
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)


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
    class TestHTTPStatusError:
        @pytest.mark.asyncio
        async def test_json_decode_failed(self) -> None:
            http = MyHTTPClient(414, {'Content-Type': 'text/plain'}, b'Error: URI Too Long')
            client = Client.from_http(http)
            with pytest.raises(http_exceptions.StatusCodeException):
                await client.request('', '')

        @pytest.mark.asyncio
        async def test_json_decode_suceeded(self) -> None:
            http = MyHTTPClient(404, {'Content-Type': 'application/json; charset=UTF-8'}, b'{"message": "Not Found", "error": 404}')
            client = Client.from_http(http)
            with pytest.raises(http_exceptions.StatusCodeException):
                await client.request('', '')

    class TestResponseContentError:
        @pytest.mark.asyncio
        async def test_UnidentifiedResponseContentError(self) -> None:
            http = MyHTTPClient(200, {}, b'{"some": "data"}')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnidentifiedResponseContentError):
                await client.request('', '')

        @pytest.mark.asyncio
        async def test_UnacceptableHTMLDocumentReceivedError(self) -> None:
            http = MyHTTPClient(200, {'Content-Type': 'text/html'}, b'<!DOCTYPE html>')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnacceptableHTMLDocumentReceivedError):
                await client.request('', '')

            http = MyHTTPClient(200, {'Content-Type': 'text/html'}, b'>user agent required</')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnacceptableHTMLDocumentReceivedError) as exc_info:
                await client.request('', '')
            assert exc_info.value.arg is not None

            http = MyHTTPClient(200, {'Content-Type': 'text/html'}, b'>Our CDN was unable to reach our servers</')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnacceptableHTMLDocumentReceivedError) as exc_info:
                await client.request('', '')
            assert exc_info.value.arg is not None

    class TestRedditAPIError:
        @pytest.mark.asyncio
        async def test_Variant2RedditAPIError(self) -> None:
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
            with pytest.raises(exceptions.Variant2RedditAPIError) as exc_info:
                await client.request('', '')
            exc = exc_info.value
            assert exc.codename == 'NO_TEXT'
            assert exc.detail == 'we need something here'
            assert exc.field == 'title'
            assert exc.errors == [
                exceptions.RedditErrorItem("NO_TEXT", "we need something here", "title"),
                exceptions.RedditErrorItem("BAD_URL", "you should check that url", "url"),
            ]

        @pytest.mark.asyncio
        async def test_Variant1RedditAPIError(self) -> None:
            b = b'''\
{
    "explanation": "Please log in to do that.",
    "message": "Forbidden",
    "reason": "USER_REQUIRED"
}
'''
            http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b)
            client = Client.from_http(http)
            with pytest.raises(exceptions.Variant1RedditAPIError) as exc_info:
                await client.request('', '')
            exc = exc_info.value
            assert exc.codename == "USER_REQUIRED"
            assert exc.detail == "Please log in to do that."
            assert exc.field == ""
            assert not exc.fields

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
            with pytest.raises(exceptions.Variant1RedditAPIError) as exc_info:
                await client.request('', '')
            exc = exc_info.value
            assert exc.codename == "TOO_LONG"
            assert exc.detail == "this is too long (max: 50)"
            assert exc.field == "title"
            assert exc.fields[0] == "title"
