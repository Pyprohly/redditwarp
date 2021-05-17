
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from ..http.requestor_decorator_SYNC import RequestorDecorator

class RequestUpdate(RequestorDecorator):
    def __init__(self, requestor: Requestor, *,
            params: Optional[Mapping[str, Optional[str]]] = None,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.params = {} if params is None else params
        self.headers = {} if headers is None else headers

    def send(self, request: Request, *, timeout: float = -2,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        request.params.update(self.params)
        request.headers.update(self.headers)
        return self.requestor.send(request, timeout=timeout, aux_info=aux_info)
