
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Mapping, List, Optional, Dict

import pytest

from redditwarp import auth
from redditwarp import core
from redditwarp.core.http_client_ASYNC import HTTPClient
from redditwarp.http.base_session_ASYNC import BaseSession
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

    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        self.history.append(request)
        return Response(self.response_status, self.response_headers, self.response_data)

@pytest.mark.asyncio
async def test_request() -> None:
    session = GoodSession(200, {}, b'')
    headers = {'cheese': 'bacon', 'fire': 'water'}
    http = HTTPClient(session=session, headers=headers)
    params: Dict[str, Optional[str]] = {'water': 'earth'}
    headers = {'fire': 'air'}
    await http.request('DELETE', 'system32', params=params, headers=headers, data={})
    requ = session.history[0]
    assert requ.verb == 'DELETE'
    assert requ.uri == 'system32'
    assert requ.params == {'raw_json': '1', 'api_type': 'json', 'water': 'earth'}
    assert requ.headers.pop('User-Agent')
    assert requ.headers == {'cheese': 'bacon', 'fire': 'air'}


class BadSession(BaseSession):
    def __init__(self,
        exc: Exception,
    ) -> None:
        super().__init__()
        self.exception = exc

    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        raise self.exception

def _get_http(session: BaseSession) -> HTTPClient:
    return HTTPClient(session=session)

class TestRequestExceptions:
    class TestAuth:
        class TestResponseContentError:
            @pytest.mark.asyncio
            async def test_UnidentifiedResponseContentError(self) -> None:
                response = Response(999, {}, b'')
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.UnidentifiedResponseContentError):
                    await http.request('', '')

            @pytest.mark.asyncio
            async def test_HTMLDocumentResponseContentError(self) -> None:
                response = Response(999, {}, b'<!doctype html>')
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.HTMLDocumentResponseContentError):
                    await http.request('', '')

            @pytest.mark.asyncio
            async def test_BlacklistedUserAgent(self) -> None:
                request = Request('', '', headers={'User-Agent': 'xscrapingx'})
                response = Response(403, {}, b'<!doctype html>', request=request)
                exc = auth.exceptions.ResponseContentError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.BlacklistedUserAgent):
                    await http.request('', '')

        class TestHTTPStatusError:
            @pytest.mark.asyncio
            async def test_incorrect_access_token_url(self) -> None:
                request = Request('GET', 'https://reddit.com/api/v1/access_token')
                response = Response(401, {}, b'', request)
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(auth.exceptions.HTTPStatusError) as exc_info:
                    await http.request('', '')
                assert exc_info.value.arg

            @pytest.mark.asyncio
            async def test_CredentialsError(self) -> None:
                response = Response(400, {}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.CredentialsError):
                    await http.request('', '')

                response = Response(401, {}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.CredentialsError):
                    await http.request('', '')

            @pytest.mark.asyncio
            async def test_InsufficientScope(self) -> None:
                response = Response(403, {'www-authenticate': 'error="insufficient_scope"'}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.InsufficientScope):
                    await http.request('', '')

                response = Response(403, {'www-authenticate': 'error="asdf"'}, b'')
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(auth.exceptions.HTTPStatusError):
                    await http.request('', '')

            @pytest.mark.asyncio
            async def test_FaultyUserAgent(self) -> None:
                request = Request('', '', headers={'User-Agent': 'xcurlx'})
                response = Response(429, {}, b'', request=request)
                exc = auth.exceptions.HTTPStatusError(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(core.exceptions.FaultyUserAgent):
                    await http.request('', '')

            @pytest.mark.asyncio
            async def test_UnsupportedGrantType(self) -> None:
                request = Request('', '', headers={'Content-Type': 'application/json'})
                response = Response(200, {}, b'', request=request)
                exc = auth.exceptions.UnsupportedGrantType(response=response)
                session = BadSession(exc)
                http = _get_http(session)
                with pytest.raises(auth.exceptions.UnsupportedGrantType) as exc_info:
                    await http.request('', '')
                assert exc_info.value.arg
