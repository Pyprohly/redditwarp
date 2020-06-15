
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
    from .request import Request
    from .response import Response

class Requestor:
    """A Requestor is a thing that makes requests."""

    def request(self, request: Request, *, timeout: Optional[float] = None,
            aux_info: Optional[Mapping] = None) -> Response:
        raise NotImplementedError

class RequestorDecorator(Requestor):
    def __init__(self, requestor: Requestor) -> None:
        self.requestor = requestor

    def request(self, request: Request, *, timeout: Optional[float] = None,
            aux_info: Optional[Mapping] = None) -> Response:
        return self.requestor.request(request, timeout=timeout, aux_info=aux_info)
