
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, List, Optional, Dict, Any

import pytest

from redditwarp import auth
from redditwarp import core
from redditwarp.core.http_client_SYNC import RedditHTTPClient
from redditwarp.http.base_session_SYNC import BaseSession
from redditwarp.http.response import Response
from redditwarp.http.request import Request

class GoodSession(BaseSession):
    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__()
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data
        self.history: List[Request] = []

    def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

class BadSession(BaseSession):
    def __init__(self,
        exc: Exception,
    ) -> None:
        super().__init__()
        self.exception = exc

    def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        raise self.exception

def test_request() -> None:
    session = GoodSession(200, {}, b'')
    headers = {'cheese': 'bacon', 'fire': 'water'}
    http = RedditHTTPClient(session=session, headers=headers)
    params: Dict[str, Optional[str]] = {'water': 'earth'}
    headers = {'fire': 'air'}
    http.request('DELETE', 'system32', params=params, headers=headers, data={})
    requ = session.history[0]
    assert requ.verb == 'DELETE'
    assert requ.uri == 'system32'
    assert requ.params == {'raw_json': '1', 'api_type': 'json', 'water': 'earth'}
    assert requ.headers.pop('User-Agent')
    assert requ.headers == {'cheese': 'bacon', 'fire': 'air'}

class TestRequestExceptions:
    class TestAuth:
        class TestResponseContentError:
            def test_UnidentifiedResponseContentError(self) -> None:
                response = Response(999, {}, b'')
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.UnidentifiedResponseContentError):
                    http.request('', '')

            def test_HTMLDocumentResponseContentError(self) -> None:
                response = Response(999, {'Content-Type': 'text/html'}, b'')
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.HTMLDocumentResponseContentError):
                    http.request('', '')

                response = Response(999, {'Content-Type': 'text/html'}, b'Our CDN was unable to reach our servers')
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.HTMLDocumentResponseContentError) as exc_info:
                    http.request('', '')
                assert exc_info.value.arg is not None

            def test_BlacklistedUserAgent(self) -> None:
                request = Request('', '', headers={'User-Agent': 'xscrapingx'})
                response = Response(403, {}, b'<!doctype html>', request=request)
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.BlacklistedUserAgent):
                    http.request('', '')

        class TestHTTPStatusError:
            def test_incorrect_access_token_url(self) -> None:
                request = Request('GET', 'https://reddit.com/api/v1/access_token')
                response = Response(401, {}, b'', request)
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(auth.exceptions.HTTPStatusError) as exc_info:
                    http.request('', '')
                assert exc_info.match('token URL')

            def test_no_authorization_header(self) -> None:
                request = Request('GET', 'https://www.reddit.com/api/v1/access_token')
                response = Response(401, {}, b'', request)
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(auth.exceptions.HTTPStatusError) as exc_info:
                    http.request('', '')
                assert exc_info.match('Authorization')

            def test_authorization_header_no_basic(self) -> None:
                request = Request('GET', 'https://www.reddit.com/api/v1/access_token', headers={'Authorization': 'asdf'})
                response = Response(401, {}, b'', request)
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(auth.exceptions.HTTPStatusError) as exc_info:
                    http.request('', '')
                assert exc_info.match('Basic')

            def test_CredentialsError(self) -> None:
                response = Response(400, {}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.CredentialsError):
                    http.request('', '')

                response = Response(401, {}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.CredentialsError):
                    http.request('', '')

            def test_InsufficientScope(self) -> None:
                session = GoodSession(403, {'WWW-Authenticate': 'error="insufficient_scope"'}, b'{"message": "Forbidden", "error": 403}')
                http = RedditHTTPClient(session=session)
                with pytest.raises(auth.exceptions.InsufficientScope):
                    http.request('', '')

            def test_FaultyUserAgent(self) -> None:
                request = Request('', '', headers={'User-Agent': 'xcurlx'})
                response = Response(429, {}, b'', request=request)
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.FaultyUserAgent):
                    http.request('', '')

            def test_UnsupportedGrantType(self) -> None:
                request = Request('', '', headers={'Content-Type': 'application/json'})
                response = Response(200, {}, b'', request=request)
                exc = auth.exceptions.UnsupportedGrantType(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(auth.exceptions.UnsupportedGrantType) as exc_info:
                    http.request('', '')
                assert exc_info.value.arg is not None
