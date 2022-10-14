
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Optional
if TYPE_CHECKING:
    from ..request import Request
    from ..response import Response

from ..requestor_ASYNC import Requestor
from ..requestor_augmenter_ASYNC import RequestorAugmenter

class DestinationNotEstablishedException(Exception):
    pass

class RequestDistributor(Requestor):
    def __init__(self) -> None:
        super().__init__()
        self.directions: MutableMapping[Request, Requestor] = {}

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        try:
            dest = self.directions[request]
        except KeyError:
            raise DestinationNotEstablishedException from None
        return await dest.send(request, timeout=timeout, follow_redirects=follow_redirects)

    def get_director(self, sender: Requestor, receiver: Requestor) -> RequestDirector:
        return RequestDirector(sender, self, receiver)

class RequestDirector(RequestorAugmenter):
    def __init__(self, requestor: Requestor, target: RequestDistributor, receiver: Requestor):
        super().__init__(requestor)
        self.target: RequestDistributor = target
        self.receiver: Requestor = receiver

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        directions = self.target.directions
        directions[request] = self.receiver
        try:
            resp = await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)
        finally:
            del directions[request]
        return resp
