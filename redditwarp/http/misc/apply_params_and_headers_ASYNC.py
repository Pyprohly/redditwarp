
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
if TYPE_CHECKING:
    from ..handler_ASYNC import Handler
    from ..send_params import SendParams
    from ..exchange import Exchange

from ..delegating_handler_ASYNC import DelegatingHandler


class ApplyParamsAndHeaders(DelegatingHandler):
    def __init__(self, handler: Handler, *,
            params: Optional[Mapping[str, str]] = None,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(handler)
        self.params: Mapping[str, str] = {} if params is None else params
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def _send(self, p: SendParams) -> Exchange:
        reqi = p.requisition
        reqi.params.update(self.params)
        reqi.headers.update(self.headers)
        return await super()._send(p)

class ApplyDefaultParamsAndHeaders(DelegatingHandler):
    def __init__(self, handler: Handler, *,
            params: Optional[Mapping[str, str]] = None,
            headers: Optional[Mapping[str, str]] = None):
        super().__init__(handler)
        self.params: Mapping[str, str] = {} if params is None else params
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def _send(self, p: SendParams) -> Exchange:
        reqi = p.requisition
        (pd := reqi.params).update({**self.params, **pd})
        (hd := reqi.headers).update({**self.headers, **hd})
        return await super()._send(p)


class ApplyParams(DelegatingHandler):
    def __init__(self, handler: Handler, params: Optional[Mapping[str, str]] = None):
        super().__init__(handler)
        self.params: Mapping[str, str] = {} if params is None else params

    async def _send(self, p: SendParams) -> Exchange:
        reqi = p.requisition
        reqi.params.update(self.params)
        return await super()._send(p)

class ApplyDefaultParams(DelegatingHandler):
    def __init__(self, handler: Handler, params: Optional[Mapping[str, str]] = None):
        super().__init__(handler)
        self.params: Mapping[str, str] = {} if params is None else params

    async def _send(self, p: SendParams) -> Exchange:
        reqi = p.requisition
        (pd := reqi.params).update({**self.params, **pd})
        return await super()._send(p)


class ApplyHeaders(DelegatingHandler):
    def __init__(self, handler: Handler, headers: Optional[Mapping[str, str]] = None):
        super().__init__(handler)
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def _send(self, p: SendParams) -> Exchange:
        reqi = p.requisition
        reqi.headers.update(self.headers)
        return await super()._send(p)

class ApplyDefaultHeaders(DelegatingHandler):
    def __init__(self, handler: Handler, headers: Optional[Mapping[str, str]] = None):
        super().__init__(handler)
        self.headers: Mapping[str, str] = {} if headers is None else headers

    async def _send(self, p: SendParams) -> Exchange:
        reqi = p.requisition
        (hd := reqi.headers).update({**self.headers, **hd})
        return await super()._send(p)
