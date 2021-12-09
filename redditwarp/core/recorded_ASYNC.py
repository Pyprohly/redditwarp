
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableSequence
if TYPE_CHECKING:
    from ..http.request import Request
    from ..http.response import Response
    from ..http.requestor_ASYNC import Requestor

from collections import deque

from ..http.requestor_augmenter_ASYNC import RequestorAugmenter

class Recorded(RequestorAugmenter):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.last_request: Optional[Request] = None
        self.last_response: Optional[Response] = None
        self.last_transfer: Optional[tuple[Request, Response]] = None
        self.last_transmit: Optional[tuple[Request, Optional[Response]]] = None
        self.last_request_queue: MutableSequence[Request] = deque(maxlen=16)
        self.last_response_queue: MutableSequence[Response] = deque(maxlen=16)
        self.last_transfer_queue: MutableSequence[tuple[Request, Response]] = deque(maxlen=16)
        self.last_transmit_queue: MutableSequence[tuple[Request, Optional[Response]]] = deque(maxlen=16)

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        resp = None
        try:
            resp = await self.requestor.send(request, timeout=timeout)
        finally:
            self.last_request = request
            self.last_transmit = (request, resp)
            self.last_request_queue.append(self.last_request)
            self.last_transmit_queue.append(self.last_transmit)
            if resp is None:
                self.last_response = None
                self.last_transfer = None
            else:
                self.last_response = resp
                self.last_transfer = (request, resp)
                self.last_response_queue.append(self.last_response)
                self.last_transfer_queue.append(self.last_transfer)

        if resp is None:
            raise Exception
        return resp

class Last:
    @property
    def request(self) -> Optional[Request]:
        return self._recorder.last_request
    @property
    def response(self) -> Optional[Response]:
        return self._recorder.last_response
    @property
    def transfer(self) -> Optional[tuple[Request, Response]]:
        return self._recorder.last_transfer
    @property
    def transmit(self) -> Optional[tuple[Request, Optional[Response]]]:
        return self._recorder.last_transmit
    @property
    def request_queue(self) -> MutableSequence[Request]:
        return self._recorder.last_request_queue
    @property
    def response_queue(self) -> MutableSequence[Response]:
        return self._recorder.last_response_queue
    @property
    def transfer_queue(self) -> MutableSequence[tuple[Request, Response]]:
        return self._recorder.last_transfer_queue
    @property
    def transmit_queue(self) -> MutableSequence[tuple[Request, Optional[Response]]]:
        return self._recorder.last_transmit_queue

    def __init__(self, recorder: Recorded) -> None:
        self._recorder = recorder

    def __abs__(self) -> Recorded:
        return self._recorder
