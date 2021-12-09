
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping
if TYPE_CHECKING:
    from ..request import Request
    from ..response import Response

from ..requestor_SYNC import Requestor
from ..requestor_augmenter_SYNC import RequestorAugmenter

class DestinationNotEstablishedException(Exception):
    pass

class RequestDistributor(Requestor):
    def __init__(self) -> None:
        super().__init__()
        self.directions: MutableMapping[Request, Requestor] = {}

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        try:
            dest = self.directions[request]
        except KeyError:
            raise DestinationNotEstablishedException from None
        return dest.send(request)

    def get_director(self, sender: Requestor, receiver: Requestor) -> RequestDirector:
        return RequestDirector(sender, self, receiver)

class RequestDirector(RequestorAugmenter):
    def __init__(self, requestor: Requestor, target: RequestDistributor, receiver: Requestor):
        super().__init__(requestor)
        self.target: RequestDistributor = target
        self.receiver: Requestor = receiver

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        directions = self.target.directions
        directions[request] = self.receiver
        try:
            resp = self.requestor.send(request)
        finally:
            del directions[request]
        return resp
