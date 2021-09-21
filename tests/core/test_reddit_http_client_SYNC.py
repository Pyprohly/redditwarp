
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import MutableMapping, List, Optional, Dict

import pytest

from redditwarp import auth
from redditwarp import core
from redditwarp.http import exceptions as http_exceptions
from redditwarp.core.reddit_http_client_SYNC import RedditHTTPClient
from redditwarp.http.session_base_SYNC import SessionBase
from redditwarp.http.response import Response
from redditwarp.http.request import Request

class GoodSession(SessionBase):
    def __init__(self,
        response_status: int,
        response_headers: MutableMapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__()
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data
        self.history: List[Request] = []

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

class NeutralSession(SessionBase):
    def __init__(self,
        response_status: int = 200,
        response_headers: Optional[MutableMapping[str, str]] = None,
        response_data: bytes = b'',
        *,
        exception: Optional[Exception] = None,
    ) -> None:
        super().__init__()
        self.response_status = response_status
        self.response_headers = {} if response_headers is None else response_headers
        self.response_data = response_data
        self.history: List[Request] = []
        self.exception = exception

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        self.history.append(request)
        if self.exception is not None:
            raise self.exception
        return Response(self.response_status, self.response_headers, self.response_data)

class BadSession(SessionBase):
    def __init__(self,
        exc: Exception,
    ) -> None:
        super().__init__()
        self.exception = exc

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        raise self.exception

def test_request() -> None:
    session = GoodSession(200, {}, b'')
    headers = {'cheese': 'bacon', 'fire': 'water'}
    http = RedditHTTPClient(session=session, headers=headers)
    params: Dict[str, str] = {'water': 'earth'}
    headers = {'fire': 'air'}
    http.request('DELETE', 'system32', params=params, headers=headers, data={})
    requ = session.history[0]
    assert requ.verb == 'DELETE'
    assert requ.uri == 'https://oauth.reddit.com/system32'
    assert requ.params == {'raw_json': '1', 'api_type': 'json', 'water': 'earth'}
    assert requ.headers.pop('User-Agent')
    assert requ.headers == {'cheese': 'bacon', 'fire': 'air'}

class TestLastMessageRecord:
    def test_last_request(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(session=session)
        assert http.last.request is None
        req1 = Request('', '')
        http.send(req1)
        assert http.last.request is req1

        session.exception = RuntimeError()
        req2 = Request('', '')
        try:
            http.send(req2)
        except RuntimeError:
            pass
        assert http.last.request is req2

        assert list(http.last.request_queue) == [req1, req2]

    def test_last_response(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(session=session)
        assert http.last.response is None
        resp = http.send(Request('', ''))
        assert http.last.response is resp

        session.exception = RuntimeError()
        try:
            http.send(Request('', ''))
        except RuntimeError:
            pass
        assert http.last.response is None

        assert list(http.last.response_queue) == [resp]

    def test_last_transfer(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(session=session)
        assert http.last.transfer is None
        req1 = Request('', '')
        resp1 = http.send(req1)
        assert http.last.transfer == (req1, resp1)

        session.exception = RuntimeError()
        try:
            http.send(Request('', ''))
        except RuntimeError:
            pass
        assert http.last.transfer is None

        assert list(http.last.transfer_queue) == [(req1, resp1)]

    def test_last_transmit(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(session=session)
        assert http.last.transmit is None
        req1 = Request('', '')
        resp1 = http.send(req1)
        assert http.last.transmit == (req1, resp1)

        session.exception = RuntimeError()
        req2 = Request('', '')
        try:
            http.send(req2)
        except RuntimeError:
            pass
        assert http.last.transmit == (req2, None)

        assert list(http.last.transmit_queue) == [(req1, resp1), (req2, None)]


class TestRequestExceptions:
    class TestHTTP:
        def test_response_exception_response_object_stored_in_last_response(self) -> None:
            response = Response(999, {}, b'')
            exc = http_exceptions.ResponseException(response=response)
            session = BadSession(exc)
            http = RedditHTTPClient(session=session)
            with pytest.raises(http_exceptions.ResponseException):
                http.request('', '')
            assert http.last_response is exc.response

    class TestAuth:
        def test_response_exception_response_object_stored_in_last_response(self) -> None:
            response = Response(999, {}, b'')
            exc = auth.exceptions.ResponseException(response=response)
            session = BadSession(exc)
            http = RedditHTTPClient(session=session)
            with pytest.raises(auth.exceptions.ResponseException):
                http.request('', '')
            assert http.last_response is exc.response

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
                response = Response(400, {}, b'{"error": "invalid_grant"}')
                exc = auth.exceptions.TokenServerResponseErrorTypes.InvalidGrant(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.CredentialsError):
                    http.request('', '')

                response = Response(401, {}, b'')
                exc2 = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc2)
                http = RedditHTTPClient(session=session)
                with pytest.raises(core.exceptions.CredentialsError):
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
                exc = auth.exceptions.TokenServerResponseErrorTypes.UnsupportedGrantType(response=response)
                session = BadSession(exc)
                http = RedditHTTPClient(session=session)
                with pytest.raises(auth.exceptions.TokenServerResponseErrorTypes.UnsupportedGrantType) as exc_info:
                    http.request('', '')
                assert exc_info.value.arg is not None
