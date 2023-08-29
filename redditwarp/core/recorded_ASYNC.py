
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableSequence
if TYPE_CHECKING:
    from ..http.handler_ASYNC import Handler
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange
    from ..http.requisition import Requisition
    from ..http.request import Request
    from ..http.response import Response

from collections import deque

from ..http.delegating_handler_ASYNC import DelegatingHandler

class Recorded(DelegatingHandler):
    def __init__(self, handler: Handler) -> None:
        super().__init__(handler)
        self.last_requisition: Optional[Requisition] = None
        ("")
        self.last_exchange: Optional[Exchange] = None
        ("")
        self.last_transmit: Optional[tuple[Requisition, Optional[Exchange]]] = None
        ("")
        self.last_transfer: Optional[tuple[Requisition, Exchange]] = None
        ("")
        self.last_request: Optional[Request] = None
        ("")
        self.last_response: Optional[Response] = None
        ("")
        self.last_requisition_queue: MutableSequence[Requisition] = deque(maxlen=16)
        ("")
        self.last_exchange_queue: MutableSequence[Exchange] = deque(maxlen=16)
        ("")
        self.last_transmit_queue: MutableSequence[tuple[Requisition, Optional[Exchange]]] = deque(maxlen=16)
        ("")
        self.last_transfer_queue: MutableSequence[tuple[Requisition, Exchange]] = deque(maxlen=16)
        ("")
        self.last_request_queue: MutableSequence[Request] = deque(maxlen=16)
        ("")
        self.last_response_queue: MutableSequence[Response] = deque(maxlen=16)
        ("")

    def clear(self) -> None:
        self.last_requisition = None
        self.last_exchange = None
        self.last_request = None
        self.last_response = None
        self.last_transmit = None
        self.last_transfer = None
        self.last_requisition_queue.clear()
        self.last_exchange_queue.clear()
        self.last_request_queue.clear()
        self.last_response_queue.clear()
        self.last_transmit_queue.clear()
        self.last_transfer_queue.clear()

    async def _send(self, p: SendParams) -> Exchange:
        exchange = None
        try:
            exchange = await super()._send(p)
        finally:
            self.last_requisition = p.requisition
            self.last_transmit = (p.requisition, exchange)
            self.last_requisition_queue.append(self.last_requisition)
            self.last_transmit_queue.append(self.last_transmit)
            if exchange is None:
                self.last_exchange = None
                self.last_request = None
                self.last_response = None
                self.last_transfer = None
            else:
                self.last_exchange = exchange
                self.last_request = exchange.request
                self.last_response = exchange.response
                self.last_transfer = (p.requisition, exchange)
                self.last_exchange_queue.append(self.last_exchange)
                self.last_request_queue.append(self.last_request)
                self.last_response_queue.append(self.last_response)
                self.last_transfer_queue.append(self.last_transfer)
        if exchange is None:
            raise Exception
        return exchange



class Last:
    @property
    def requisition(self) -> Optional[Requisition]:
        return self.recorder.last_requisition
    @property
    def exchange(self) -> Optional[Exchange]:
        return self.recorder.last_exchange
    @property
    def request(self) -> Optional[Request]:
        return self.recorder.last_request
    @property
    def response(self) -> Optional[Response]:
        return self.recorder.last_response
    @property
    def transmit(self) -> Optional[tuple[Requisition, Optional[Exchange]]]:
        return self.recorder.last_transmit
    @property
    def transfer(self) -> Optional[tuple[Requisition, Exchange]]:
        return self.recorder.last_transfer
    @property
    def requisition_queue(self) -> MutableSequence[Requisition]:
        return self.recorder.last_requisition_queue
    @property
    def exchange_queue(self) -> MutableSequence[Exchange]:
        return self.recorder.last_exchange_queue
    @property
    def request_queue(self) -> MutableSequence[Request]:
        return self.recorder.last_request_queue
    @property
    def response_queue(self) -> MutableSequence[Response]:
        return self.recorder.last_response_queue
    @property
    def transmit_queue(self) -> MutableSequence[tuple[Requisition, Optional[Exchange]]]:
        return self.recorder.last_transmit_queue
    @property
    def transfer_queue(self) -> MutableSequence[tuple[Requisition, Exchange]]:
        return self.recorder.last_transfer_queue

    def clear(self) -> None:
        self.recorder.clear()

    def __init__(self, recorder: Recorded) -> None:
        self.recorder: Recorded = recorder
