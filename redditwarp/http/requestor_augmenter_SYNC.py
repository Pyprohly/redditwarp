
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .request import Request
    from .response import Response

from .requestor_SYNC import Requestor

class RequestorAugmenter(Requestor):
    def __init__(self, requestor: Requestor) -> None:
        self.requestor: Requestor = requestor

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        return self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)
