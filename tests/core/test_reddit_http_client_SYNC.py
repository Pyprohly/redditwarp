
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import MutableMapping, Optional, MutableSequence

from redditwarp.core.reddit_http_client_SYNC import RedditHTTPClient
from redditwarp.http.handler_SYNC import Handler
from redditwarp.http.delegating_handler_SYNC import DelegatingHandler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.requisition import Requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response


class NeutralHandler(Handler):
    DUMMY_REQUISITION = Requisition('', '', {}, {}, None)
    DUMMY_REQUEST = Request('', '', {})

    def __init__(self,
        response_status: int,
        response_headers: MutableMapping[str, str],
        response_data: bytes,
        *,
        exception: Optional[Exception] = None,
    ) -> None:
        super().__init__()
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data
        self.exception = exception

    def _send(self, p: SendParams) -> Exchange:
        if self.exception is not None:
            raise self.exception
        resp = Response(self.response_status, self.response_headers, self.response_data)
        return Exchange(
            requisition=self.DUMMY_REQUISITION,
            request=self.DUMMY_REQUEST,
            response=resp,
            history=(),
        )

class RecordingHandler(DelegatingHandler):
    def __init__(self, handler: Handler) -> None:
        super().__init__(handler)
        self.history: MutableSequence[Requisition] = []

    def _send(self, p: SendParams) -> Exchange:
        self.history.append(p.requisition)
        return super()._send(p)


def test_request() -> None:
    recorder = RecordingHandler(NeutralHandler(200, {}, b''))
    headers = {'a': '1', 'b': '2'}
    http = RedditHTTPClient(recorder, headers=headers)
    params = {'b': '2', 'c': '3'}
    headers = {'b': '2', 'c': '3'}
    http.request('DELETE', 'system32', params=params, headers=headers, data={})
    reqi = recorder.history[0]
    assert reqi.verb == 'DELETE'
    assert reqi.url == 'https://oauth.reddit.com/system32'
    assert reqi.params == {'b': '2', 'c': '3'}
    assert reqi.headers == {'a': '1', 'b': '2', 'c': '3'}

class TestLastMessageRecord:
    BLANK_REQUISITION = Requisition('', '', {}, {}, None)

    def test_last_requisition(self) -> None:
        handler = NeutralHandler(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(handler)
        assert http.last.requisition is None
        req1 = self.BLANK_REQUISITION
        http.submit(req1)
        assert http.last.requisition is req1

        handler.exception = RuntimeError()
        req2 = self.BLANK_REQUISITION
        try:
            http.submit(req2)
        except RuntimeError:
            pass
        assert http.last.requisition == req2

        assert list(http.last.requisition_queue) == [req1, req2]

    def test_last_exchange(self) -> None:
        handler = NeutralHandler(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(handler)
        assert http.last.exchange is None
        xchg = http.submit(self.BLANK_REQUISITION)
        assert http.last.exchange is xchg

        handler.exception = RuntimeError()
        try:
            http.submit(self.BLANK_REQUISITION)
        except RuntimeError:
            pass
        assert http.last.exchange is None

        assert list(http.last.exchange_queue) == [xchg]

    def test_last_transmit(self) -> None:
        handler = NeutralHandler(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(handler)
        assert http.last.transmit is None
        req1 = self.BLANK_REQUISITION
        xchg1 = http.submit(req1)
        assert http.last.transmit == (req1, xchg1)

        handler.exception = RuntimeError()
        req2 = self.BLANK_REQUISITION
        try:
            http.submit(req2)
        except RuntimeError:
            pass
        assert http.last.transmit == (req2, None)

        assert list(http.last.transmit_queue) == [(req1, xchg1), (req2, None)]

    def test_last_transfer(self) -> None:
        handler = NeutralHandler(200, {'Content-Type': 'text/html'}, b'{"a": 1}')
        http = RedditHTTPClient(handler)
        assert http.last.transfer is None
        req1 = self.BLANK_REQUISITION
        xchg1 = http.submit(req1)
        assert http.last.transfer == (req1, xchg1)

        handler.exception = RuntimeError()
        try:
            http.submit(self.BLANK_REQUISITION)
        except RuntimeError:
            pass
        assert http.last.transfer is None

        assert list(http.last.transfer_queue) == [(req1, xchg1)]
