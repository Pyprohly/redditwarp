
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableSequence
if TYPE_CHECKING:
    from ..http.request import Request
    from ..http.response import Response
    from ..http.requestor_ASYNC import Requestor

from collections import deque

from .. import http
from .. import auth
from ..http.requestor_decorator_ASYNC import RequestorDecorator

class RecordMessages(RequestorDecorator):
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
        except Exception as e:
            resp = self.extract_response_from_exception(e)
            raise
        finally:
            self.last_request = request
            self.last_transmit = (request, resp)
            self.last_request_queue.append(request)
            self.last_transmit_queue.append(self.last_transmit)
            if resp is None:
                self.last_response = None
                self.last_transfer = None
            else:
                self.last_response = resp
                self.last_transfer = (request, resp)
                self.last_response_queue.append(resp)
                self.last_transfer_queue.append(self.last_transfer)

        if resp is None:
            raise Exception
        return resp

    def extract_response_from_exception(self, e: Exception) -> Optional[Response]:
        exception_classes = (
            http.exceptions.ResponseException,
            auth.exceptions.ResponseException,
        )
        if isinstance(e, exception_classes):
            return e.response
        return None


class RecordLastMessages(RequestorDecorator):
    class State:
        def __init__(self) -> None:
            self.request: Optional[Request] = None
            self.response: Optional[Response] = None
            self.transfer: Optional[tuple[Request, Response]] = None
            self.transmit: Optional[tuple[Request, Optional[Response]]] = None
            self.request_queue: MutableSequence[Request] = deque(maxlen=16)
            self.response_queue: MutableSequence[Response] = deque(maxlen=16)
            self.transfer_queue: MutableSequence[tuple[Request, Response]] = deque(maxlen=16)
            self.transmit_queue: MutableSequence[tuple[Request, Optional[Response]]] = deque(maxlen=16)

    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.last = self.State()

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        resp = None
        try:
            resp = await self.requestor.send(request, timeout=timeout)
        except Exception as e:
            resp = self.extract_response_from_exception(e)
            raise
        finally:
            self.last.request = request
            self.last.transmit = (request, resp)
            self.last.request_queue.append(request)
            self.last.transmit_queue.append(self.last.transmit)
            if resp is None:
                self.last.response = None
                self.last.transfer = None
            else:
                self.last.response = resp
                self.last.transfer = (request, resp)
                self.last.response_queue.append(resp)
                self.last.transfer_queue.append(self.last.transfer)

        if resp is None:
            raise Exception
        return resp

    def extract_response_from_exception(self, e: Exception) -> Optional[Response]:
        exception_classes = (
            http.exceptions.ResponseException,
            auth.exceptions.ResponseException,
        )
        if isinstance(e, exception_classes):
            return e.response
        return None
