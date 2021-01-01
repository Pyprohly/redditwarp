
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Any
if TYPE_CHECKING:
    from .request import Request
    from .response import Response

from .requestor_ASYNC import Requestor
from .requestor_decorator_ASYNC import RequestorDecorator

class NoDestinationException(Exception):
    pass

class RequestorDecoratorDemux(Requestor):
    def __init__(self) -> None:
        super().__init__()
        self.selections: MutableMapping[Request, Requestor] = {}

    async def send(self, request: Request, *, timeout: float = 0,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        try:
            sel = self.selections[request]
        except KeyError:
            raise NoDestinationException from None
        return await sel.send(request)

    def get_selector(self,
        rd: RequestorDecorator, destination: Requestor
    ) -> RequestorDecoratorDemuxDestinationSelector:
        return RequestorDecoratorDemuxDestinationSelector(rd, self, destination)

class RequestorDecoratorDemuxDestinationSelector(RequestorDecorator):
    def __init__(self, requestor: Requestor, receiver: RequestorDecoratorDemux, destination: Requestor):
        super().__init__(requestor)
        self.receiver = receiver
        self.destination = destination

    async def send(self, request: Request, *, timeout: float = 0,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        selections = self.receiver.selections
        selections[request] = self.destination
        try:
            resp = await self.requestor.send(request)
        finally:
            del selections[request]
        return resp
