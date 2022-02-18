
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import MutableMapping, List, Optional, Dict

from redditwarp.core.reddit_http_client_SYNC import RedditHTTPClient
from redditwarp.core.recorded_SYNC import Recorded, Last
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
        self.exception = exception

    def send(self, request: Request, *, timeout: float = -2) -> Response:
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
    blank_request = Request('', '', params={}, headers={}, payload=None)

    def test_last_request(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        recorder = Recorded(session)
        last = Last(recorder)
        http = RedditHTTPClient(session=session, requestor=recorder, last=last)
        assert http.last.request is None
        req1 = self.blank_request
        http.send(req1)
        assert http.last.request is req1

        session.exception = RuntimeError()
        req2 = self.blank_request
        try:
            http.send(req2)
        except RuntimeError:
            pass
        assert http.last.request is req2

        assert list(http.last.request_queue) == [req1, req2]

    def test_last_response(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        recorder = Recorded(session)
        last = Last(recorder)
        http = RedditHTTPClient(session=session, requestor=recorder, last=last)
        assert http.last.response is None
        resp = http.send(self.blank_request)
        assert http.last.response is resp

        session.exception = RuntimeError()
        try:
            http.send(self.blank_request)
        except RuntimeError:
            pass
        assert http.last.response is None

        assert list(http.last.response_queue) == [resp]

    def test_last_transfer(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        recorder = Recorded(session)
        last = Last(recorder)
        http = RedditHTTPClient(session=session, requestor=recorder, last=last)
        assert http.last.transfer is None
        req1 = self.blank_request
        resp1 = http.send(req1)
        assert http.last.transfer == (req1, resp1)

        session.exception = RuntimeError()
        try:
            http.send(self.blank_request)
        except RuntimeError:
            pass
        assert http.last.transfer is None

        assert list(http.last.transfer_queue) == [(req1, resp1)]

    def test_last_transmit(self) -> None:
        session = NeutralSession(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        recorder = Recorded(session)
        last = Last(recorder)
        http = RedditHTTPClient(session=session, requestor=recorder, last=last)
        assert http.last.transmit is None
        req1 = self.blank_request
        resp1 = http.send(req1)
        assert http.last.transmit == (req1, resp1)

        session.exception = RuntimeError()
        req2 = self.blank_request
        try:
            http.send(req2)
        except RuntimeError:
            pass
        assert http.last.transmit == (req2, None)

        assert list(http.last.transmit_queue) == [(req1, resp1), (req2, None)]
