
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Any
if TYPE_CHECKING:
    from redditwarp.http.request import Request
    from redditwarp.http.payload import Payload

import pytest  # type: ignore[import]

from redditwarp import exceptions
from redditwarp.client_async import Client
from redditwarp.core.http_client_async import HTTPClient
from redditwarp.http.base_session_async import BaseSession
from redditwarp.http.response import Response

class MySession(BaseSession):
    async def request(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        return Response(0, {}, b'')

class MyHTTPClient(HTTPClient):
    session = MySession()

    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__(session=self.session, requestor=self.session, authorized_requestor=None)
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[MutableMapping[str, str]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[MutableMapping[str, str]] = None,
        timeout: float = 8,
        aux_info: Optional[Mapping] = None,
    ) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)


@pytest.mark.asyncio
async def test_request() -> None:
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"some": "data"}')
    client = Client.from_http(http)
    assert client.last_response is None
    data = await client.request('', '')
    assert data == {"some": "data"}
    assert client.last_response is not None

class TestRequestExceptions:
    class TestResponseContentError:
        @pytest.mark.asyncio
        async def test_UnidentifiedResponseContentError(self) -> None:
            http = MyHTTPClient(200, {}, b'{"some": "data"}')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnidentifiedResponseContentError):
                await client.request('', '')

        @pytest.mark.asyncio
        async def test_HTMLDocumentReceivedError(self) -> None:
            http = MyHTTPClient(200, {}, b'<!DOCTYPE html>')
            client = Client.from_http(http)
            with pytest.raises(exceptions.HTMLDocumentReceivedError):
                await client.request('', '')

            http = MyHTTPClient(200, {}, b'<!DOCTYPE html>' + b'>user agent required</')
            client = Client.from_http(http)
            with pytest.raises(exceptions.HTMLDocumentReceivedError) as exc_info:
                await client.request('', '')
            assert exc_info.value.exc_msg is not None

        @pytest.mark.asyncio
        async def test_UnacceptableResponseContentError(self) -> None:
            http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"jquery": {}, "success": false}')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnacceptableJSONLayoutResponseContentError):
                await client.request('', '')

    class TestRedditAPIError:
        @pytest.mark.asyncio
        async def test_RedditAPIErrorVariant1(self) -> None:
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
            with pytest.raises(exceptions.RedditAPIErrorVariant1) as exc_info:
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
        async def test_RedditAPIErrorVariant2(self) -> None:
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
            with pytest.raises(exceptions.RedditAPIErrorVariant2) as exc_info:
                await client.request('', '')
            exc = exc_info.value
            assert exc.codename == "TOO_LONG"
            assert exc.detail == "this is too long (max: 50)"
            assert exc.field == "title"
            assert exc.fields == ["title"]
