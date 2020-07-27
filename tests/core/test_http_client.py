
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, List, Optional

import pytest  # type: ignore[import]

from redditwarp import auth
from redditwarp import core
from redditwarp.core.http_client_sync import HTTPClient
from redditwarp.http.base_session_sync import BaseSession
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
            aux_info: Optional[Mapping] = None) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

def test_request() -> None:
    session = GoodSession(200, {}, b'')
    default_headers = {'cheese': 'bacon', 'fire': 'water'}
    http = HTTPClient(
        session=session,
        requestor=session,
        default_headers=default_headers,
        authorized_requestor=None,
    )
    params = {'water': 'earth'}
    headers = {'fire': 'air'}
    http.request('DELETE', 'system32', params=params, headers=headers, data={})
    requ = session.history[0]
    assert requ.verb == 'DELETE'
    assert requ.uri == 'system32'
    assert requ.params is params
    assert requ.params == {'raw_json': '1', 'api_type': 'json', 'water': 'earth'}
    assert requ.headers.pop('User-Agent')
    assert requ.headers == {'cheese': 'bacon', 'fire': 'air'}


class BadSession(BaseSession):
    def __init__(self,
        exc: Exception,
    ) -> None:
        super().__init__()
        self.exception = exc

    def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        raise self.exception

def _get_http(session: BaseSession) -> HTTPClient:
    return HTTPClient(
        session=session,
        requestor=session,
        authorized_requestor=None,
    )

class TestRequestExceptions:
    class TestAuth:
        class TestResponseContentError:
            def test_UnidentifiedResponseContentError(self) -> None:
                response = Response(999, {}, b'')
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.UnidentifiedResponseContentError):
                    http.request('', '')

            def test_HTMLDocumentResponseContentError(self) -> None:
                response = Response(999, {}, b'<!doctype html>')
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.HTMLDocumentResponseContentError):
                    http.request('', '')

            def test_BlacklistedUserAgent(self) -> None:
                request = Request('', '', headers={'User-Agent': 'xscrapingx'})
                response = Response(403, {}, b'<!doctype html>', request=request)
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.BlacklistedUserAgent):
                    http.request('', '')

        class TestHTTPStatusError:
            def test_CredentialsError(self) -> None:
                response = Response(400, {}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.CredentialsError):
                    http.request('', '')

                response = Response(401, {}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.CredentialsError):
                    http.request('', '')

            def test_InsufficientScope(self) -> None:
                response = Response(403, {'www-authenticate': 'error="insufficient_scope"'}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.InsufficientScope):
                    http.request('', '')

                response = Response(403, {'www-authenticate': 'error="asdf"'}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(auth.exceptions.HTTPStatusError):
                    http.request('', '')

            def test_FaultyUserAgent(self) -> None:
                request = Request('', '', headers={'User-Agent': 'xcurlx'})
                response = Response(429, {}, b'', request=request)
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.FaultyUserAgent):
                    http.request('', '')
