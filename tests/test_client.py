
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Any
if TYPE_CHECKING:
    from redditwarp.http.request import Request
    from redditwarp.http.payload import Payload

import pytest

from redditwarp import exceptions
from redditwarp.client_sync import Client
from redditwarp.core.http_client_sync import HTTPClient
from redditwarp.http.base_session_sync import BaseSession
from redditwarp.http.response import Response

class MySession(BaseSession):
    def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        return Response(0, {}, b'')

class MyHTTPClient(HTTPClient):
    session = MySession()

    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__(session=self.session)
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[MutableMapping[str, str]] = None,
        timeout: float = 8,
        aux_info: Optional[Mapping] = None,
    ) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)


def test_request() -> None:
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"some": "data"}')
    client = Client.from_http(http)
    assert client.last_response is None
    data = client.request('', '')
    assert data == {"some": "data"}
    assert client.last_response is not None

class TestRequestExceptions:
    class TestHTTPStatusError:
        def test_json_decode_failed(self) -> None:
            http = MyHTTPClient(414, {'Content-Type': 'text/plain'}, b'Error: URI Too Long')
            client = Client.from_http(http)
            with pytest.raises(exceptions.HTTPStatusError):
                client.request('', '')

        def test_json_decode_suceeded(self) -> None:
            http = MyHTTPClient(404, {'Content-Type': 'application/json; charset=UTF-8'}, b'{"message": "Not Found", "error": 404}')
            client = Client.from_http(http)
            with pytest.raises(exceptions.HTTPStatusError):
                client.request('', '')

    class TestResponseContentError:
        def test_UnidentifiedResponseContentError(self) -> None:
            http = MyHTTPClient(200, {}, b'{"some": "data"}')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnidentifiedResponseContentError):
                client.request('', '')

        def test_UnacceptableHTMLDocumentReceivedError(self) -> None:
            http = MyHTTPClient(200, {'Content-Type': 'text/html'}, b'<!DOCTYPE html>')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnacceptableHTMLDocumentReceivedError):
                client.request('', '')

            http = MyHTTPClient(200, {'Content-Type': 'text/html'}, b'<!DOCTYPE html>' + b'>user agent required</')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnacceptableHTMLDocumentReceivedError) as exc_info:
                client.request('', '')
            assert exc_info.value.arg is not None

        def test_UnacceptableResponseContentError(self) -> None:
            http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"jquery": {}, "success": false}')
            client = Client.from_http(http)
            with pytest.raises(exceptions.UnacceptableJSONLayoutResponseContentError):
                client.request('', '')

    class TestRedditAPIError:
        def test_Variant2RedditAPIError(self) -> None:
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
                client.request('', '')
            exc = exc_info.value
            assert exc.codename == 'NO_TEXT'
            assert exc.detail == 'we need something here'
            assert exc.field == 'title'
            assert exc.errors == [
                exceptions.RedditErrorItem("NO_TEXT", "we need something here", "title"),
                exceptions.RedditErrorItem("BAD_URL", "you should check that url", "url"),
            ]

        def test_Variant1RedditAPIError(self) -> None:
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
                client.request('', '')
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
                client.request('', '')
            exc = exc_info.value
            assert exc.codename == "TOO_LONG"
            assert exc.detail == "this is too long (max: 50)"
            assert exc.field == "title"
            assert exc.fields == ["title"]
