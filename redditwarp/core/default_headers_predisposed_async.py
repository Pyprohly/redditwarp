
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
    from ..http.requestor_async import Requestor
    from ..http.request import Request
    from ..http.response import Response

from ..http.requestor_async import RequestorDecorator

class DefaultHeadersPredisposed(RequestorDecorator):
    def __init__(self, requestor: Requestor, headers: Optional[Mapping[str, str]]):
        super().__init__(requestor)
        self.headers = headers

    async def request(self, request: Request, *, timeout: Optional[float] = None,
            aux_info: Optional[Mapping] = None) -> Response:
        if self.headers:
            h = request.headers
            h.update({**self.headers, **h})
        return await self.requestor.request(request, timeout=timeout, aux_info=aux_info)
