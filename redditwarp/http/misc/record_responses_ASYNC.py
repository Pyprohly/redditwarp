
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableSequence
if TYPE_CHECKING:
    from ..request import Request
    from ..response import Response
    from ..requestor_ASYNC import Requestor

import collections

from ..requestor_decorator_ASYNC import RequestorDecorator

class RecordResponses(RequestorDecorator):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.responses: MutableSequence[Response] = collections.deque(maxlen=12)
        self.last_response: Optional[Response] = None

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        resp = await self.requestor.send(request, timeout=timeout)
        self.last_response = resp
        self.responses.append(resp)
        return resp