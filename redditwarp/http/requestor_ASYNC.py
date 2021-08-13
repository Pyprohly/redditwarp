
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .request import Request
    from .response import Response

class Requestor:
    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        raise NotImplementedError
