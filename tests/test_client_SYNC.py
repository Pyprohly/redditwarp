
from __future__ import annotations
from typing import Mapping

import pytest

from redditwarp import exceptions
from redditwarp.http import exceptions as http_exceptions
from redditwarp.client_SYNC import Client
from redditwarp.core.reddit_http_client_SYNC import RedditHTTPClient
from redditwarp.http.handler_SYNC import Handler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.requisition import Requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response


class MyHTTPClient(RedditHTTPClient):
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

    def send(self, p: SendParams) -> Exchange:
        resp = Response(self.response_status, self.response_headers, self.response_data)
        return Exchange(
            requisition=self.DUMMY_REQUISITION,
            request=self.DUMMY_REQUEST,
            response=resp,
            history=(),
        )


def test_request() -> None:
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"some": "data"}')
    client = Client.from_http(http)
    data = client.request('', '')
    assert data == {"some": "data"}

def test_zero_data() -> None:
    # Test None is returned on zero data even when Content-Type is 'application/json'.
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'')
    client = Client.from_http(http)
    data = client.request('', '')
    assert data is None

def test_last_value() -> None:
    http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'{"a": 1}')
    client = Client.from_http(http)
    client.request('', '')
    assert client.last_value == {'a': 1}
    http.response_data = b''
    client.request('', '')
    assert client.last_value is None

class TestRequestExceptions:
    def test_json_decode_failed_and_status_code_exception(self) -> None:
        http = MyHTTPClient(414, {'Content-Type': 'text/plain'}, b'Error: URI Too Long')
        client = Client.from_http(http)
        with pytest.raises(http_exceptions.StatusCodeException):
            client.request('', '')

    def test_json_decode_succeeded_but_status_code_exception(self) -> None:
        http = MyHTTPClient(404, {'Content-Type': 'application/json; charset=UTF-8'}, b'{"message": "Not Found", "error": 404}')
        client = Client.from_http(http)
        with pytest.raises(http_exceptions.StatusCodeException):
            client.request('', '')

    def test_no_content_type_in_response(self) -> None:
        http = MyHTTPClient(200, {}, b'{"some": "data"}')
        client = Client.from_http(http)
        with pytest.raises(ValueError):
            client.request('', '')

    def test_non_json_response(self) -> None:
        http = MyHTTPClient(200, {'Content-Type': 'text/html'}, b'<!DOCTYPE html>')
        client = Client.from_http(http)
        with pytest.raises(ValueError):
            client.request('', '')

        http = MyHTTPClient(403, {'Content-Type': 'text/html'}, b'>user agent required</')
        client = Client.from_http(http)
        with pytest.raises(exceptions.UserAgentRequired) as exc_info:
            client.request('', '')
        assert exc_info.value.arg is not None

        sample = b'''
<!doctype html>
<html><head><title>Ow! -- reddit.com</title>
  <script type="text/javascript">
    // send metric to our internal tracker.
    function makeRequest(url, data) {
      var dataString;
      try {
        dataString = JSON.stringify(data);
      } catch (e) {
        return false;
      }
      if (window.XMLHttpRequest) {
        httpRequest = new XMLHttpRequest();
      } else if (window.ActiveXObject) {
        try {
          httpRequest = new ActiveXObject("Msxml2.XMLHTTP");
        }
        catch (e) {
          try {
            httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
          }
          catch (e) {}
        }
      }
      if (!httpRequest) {
        return false;
      }
      httpRequest.open('POST', url);
      httpRequest.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
      httpRequest.send(dataString);
    }
    makeRequest('https://stats.redditmedia.com', {cdnError:{error50x:1,}});
  </script>
<style>
body{text-align:center;position:absolute;top:50%;margin:0;margin-top:-275px;width:100%}
h2,h3{color:#555;font:bold 200%/100px sans-serif;margin:0}
h3{color:#777;font:normal 150% sans-serif}
</style>
</head>
<img src=//redditstatic.s3.amazonaws.com/heavy-load.png alt="">
<h2>Our CDN was unable to reach our servers</h2>
Please check <a href="http://www.redditstatus.com/">www.redditstatus.com</a> if you consistently get this error.
'''
        http = MyHTTPClient(500, {'Content-Type': 'text/html'}, sample)
        client = Client.from_http(http)
        with pytest.raises(http_exceptions.StatusCodeException) as exc_info1:
            client.request('', '')
        assert isinstance(arg := exc_info1.value.arg, str) and 'CDN' in arg

    def test_variant1_reddit_error(self) -> None:
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
            client.request('', '')
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
            client.request('', '')
        exc = exc_info.value
        assert exc.label == "TOO_LONG"
        assert exc.explanation == "this is too long (max: 50)"
        assert exc.field == "title"

    def test_variant2_reddit_error(self) -> None:
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
            client.request('', '')
        exc = exc_info.value
        assert exc.label == 'NO_TEXT'
        assert exc.explanation == 'we need something here'
        assert exc.field == 'title'
