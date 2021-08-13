
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
    from ..requestor_SYNC import Requestor
    from ..request import Request
    from ..response import Response

from ..requestor_decorator_SYNC import RequestorDecorator

class ApplyParamsAndHeaders(RequestorDecorator):
    def __init__(self, requestor: Requestor, *,
            params: Optional[Mapping[str, Optional[str]]] = None,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.params = {} if params is None else params
        self.headers = {} if headers is None else headers

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        request.params.update(self.params)
        request.headers.update(self.headers)
        return self.requestor.send(request, timeout=timeout)

class ApplyDefaultParamsAndHeaders(RequestorDecorator):
    def __init__(self, requestor: Requestor, *,
            params: Optional[Mapping[str, Optional[str]]] = None,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.params = {} if params is None else params
        self.headers = {} if headers is None else headers

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        (pd := request.params).update({**self.params, **pd})
        (hd := request.headers).update({**self.headers, **hd})
        return self.requestor.send(request, timeout=timeout)
