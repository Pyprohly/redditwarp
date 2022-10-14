
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
    from ..requestor_ASYNC import Requestor
    from ..request import Request
    from ..response import Response

from ..requestor_augmenter_ASYNC import RequestorAugmenter

class ApplyParamsAndHeaders(RequestorAugmenter):
    def __init__(self, requestor: Requestor, *,
            params: Optional[Mapping[str, str]] = None,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.params: Mapping[str, str] = {} if params is None else params
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        request.params.update(self.params)
        request.headers.update(self.headers)
        return await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)

class ApplyDefaultParamsAndHeaders(RequestorAugmenter):
    def __init__(self, requestor: Requestor, *,
            params: Optional[Mapping[str, str]] = None,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.params: Mapping[str, str] = {} if params is None else params
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        (pd := request.params).update({**self.params, **pd})
        (hd := request.headers).update({**self.headers, **hd})
        return await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)



class ApplyParams(RequestorAugmenter):
    def __init__(self, requestor: Requestor, params: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.params: Mapping[str, str] = {} if params is None else params

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        request.params.update(self.params)
        return await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)

class ApplyDefaultParams(RequestorAugmenter):
    def __init__(self, requestor: Requestor, params: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.params: Mapping[str, str] = {} if params is None else params

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        (pd := request.params).update({**self.params, **pd})
        return await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)



class ApplyHeaders(RequestorAugmenter):
    def __init__(self, requestor: Requestor, headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        request.headers.update(self.headers)
        return await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)

class ApplyDefaultHeaders(RequestorAugmenter):
    def __init__(self, requestor: Requestor, headers: Optional[Mapping[str, str]] = None):
        super().__init__(requestor)
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        (hd := request.headers).update({**self.headers, **hd})
        return await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)
