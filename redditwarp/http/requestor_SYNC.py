
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .request import Request
    from .response import Response

class Requestor:
    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        raise NotImplementedError
