
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .request import Request
    from .response import Response

from .requestor_ASYNC import Requestor

class RequestorDecorator(Requestor):
    def __init__(self, requestor: Requestor) -> None:
        self.requestor: Requestor = requestor

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        return await self.requestor.send(request, timeout=timeout)
