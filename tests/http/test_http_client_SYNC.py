
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import MutableMapping, Optional, MutableSequence

from redditwarp.core.http_client_SYNC import HTTPClient
from redditwarp.http.handler_SYNC import Handler
from redditwarp.http.delegating_handler_SYNC import DelegatingHandler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.requisition import Requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import MultipartFormData


class NeutralHandler(Handler):
    DUMMY_REQUISITION = Requisition('', '', {}, {}, None)
    DUMMY_REQUEST = Request('', '', {}, b'')

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


def test_data_and_files_are_combined_in_correct_order() -> None:
    recorder = RecordingHandler(NeutralHandler(200, {}, b''))
    http = HTTPClient(recorder)
    http.request('DELETE', 'system32', data={'a': '1'}, files={'b': '2'})
    reqi = recorder.history[0]
    pld = reqi.payload
    assert isinstance(pld, MultipartFormData)
    assert [pt.name for pt in pld.parts] == ['a', 'b']
