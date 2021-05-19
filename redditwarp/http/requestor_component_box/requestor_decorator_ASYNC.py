
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..request import Request
    from ..response import Response

from ..requestor_ASYNC import Requestor

class RequestorDecorator(Requestor):
    def __init__(self, requestor: Requestor) -> None:
        self.requestor = requestor

    async def send(self, request: Request, *, timeout: float = -2,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        return await self.requestor.send(request, timeout=timeout, aux_info=aux_info)
