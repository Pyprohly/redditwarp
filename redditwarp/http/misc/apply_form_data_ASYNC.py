
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, final
if TYPE_CHECKING:
    from ..handler_ASYNC import Handler
    from ..send_params import SendParams
    from ..exchange import Exchange
    from ..types import RequestFiles

from collections.abc import MutableMapping, MutableSequence

from ..delegating_handler_ASYNC import DelegatingHandler
from ..payload import URLEncodedFormData, MultipartFormData, make_multipart_parts_from_request_files


@final
class ApplyFormData(DelegatingHandler):
    def __init__(self, handler: Handler, data: Mapping[str, str]) -> None:
        super().__init__(handler)
        self._data: Mapping[str, str] = data
        parts = make_multipart_parts_from_request_files(data)
        self._d: Mapping[str, MultipartFormData.Field] = {p.name: p for p in parts}

    async def _send(self, p: SendParams) -> Exchange:
        pld = p.requisition.payload
        if isinstance(pld, URLEncodedFormData):
            data = pld.data
            if not isinstance(data, MutableMapping):
                raise RuntimeError('payload is non-mutable')
            data.update(self._data)
        elif isinstance(pld, MultipartFormData):
            parts = pld.parts
            if not isinstance(parts, MutableSequence):
                raise RuntimeError('payload is non-mutable')
            d = {p.name: p for p in parts}
            d.update(self._d)
            parts.clear()
            parts.extend(d.values())
        else:
            raise RuntimeError('payload is not form data')
        return await super()._send(p)

@final
class ApplyDefaultFormData(DelegatingHandler):
    def __init__(self, handler: Handler, data: Mapping[str, str]) -> None:
        super().__init__(handler)
        self._data: Mapping[str, str] = data
        parts = make_multipart_parts_from_request_files(data)
        self._d: Mapping[str, MultipartFormData.Field] = {p.name: p for p in parts}

    async def _send(self, p: SendParams) -> Exchange:
        pld = p.requisition.payload
        if isinstance(pld, URLEncodedFormData):
            data = pld.data
            if not isinstance(data, MutableMapping):
                raise RuntimeError('payload is non-mutable')
            data.update({**self._data, **data})
        elif isinstance(pld, MultipartFormData):
            parts = pld.parts
            if not isinstance(parts, MutableSequence):
                raise RuntimeError('payload is non-mutable')
            d = {p.name: p for p in parts}
            d.update({**self._d, **d})
            parts.clear()
            parts.extend(d.values())
        else:
            raise RuntimeError('payload is not form data')
        return await super()._send(p)


@final
class ApplyURLEncodedFormData(DelegatingHandler):
    def __init__(self, handler: Handler, data: Mapping[str, str]) -> None:
        super().__init__(handler)
        self._data: Mapping[str, str] = data

    async def _send(self, p: SendParams) -> Exchange:
        pld = p.requisition.payload
        if not isinstance(pld, URLEncodedFormData):
            raise RuntimeError('payload is not URL-encoded form data')
        data = pld.data
        if not isinstance(data, MutableMapping):
            raise RuntimeError('payload is non-mutable')
        data.update(self._data)
        return await super()._send(p)

@final
class ApplyDefaultURLEncodedFormData(DelegatingHandler):
    def __init__(self, handler: Handler, data: Mapping[str, str]) -> None:
        super().__init__(handler)
        self._data: Mapping[str, str] = data

    async def _send(self, p: SendParams) -> Exchange:
        pld = p.requisition.payload
        if not isinstance(pld, URLEncodedFormData):
            raise RuntimeError('payload is not URL-encoded form data')
        data = pld.data
        if not isinstance(data, MutableMapping):
            raise RuntimeError('payload is non-mutable')
        data.update({**self._data, **data})
        return await super()._send(p)


@final
class ApplyMultipartFormData(DelegatingHandler):
    def __init__(self, handler: Handler, data: RequestFiles) -> None:
        parts = make_multipart_parts_from_request_files(data)
        self._d: Mapping[str, MultipartFormData.Field] = {p.name: p for p in parts}

    async def _send(self, p: SendParams) -> Exchange:
        pld = p.requisition.payload
        if not isinstance(pld, MultipartFormData):
            raise RuntimeError('payload is not multipart form data')
        parts = pld.parts
        if not isinstance(parts, MutableSequence):
            raise RuntimeError('payload is non-mutable')
        d = {p.name: p for p in parts}
        d.update(self._d)
        parts.clear()
        parts.extend(d.values())
        return await super()._send(p)

@final
class ApplyDefaultMultipartFormData(DelegatingHandler):
    def __init__(self, handler: Handler, data: RequestFiles) -> None:
        super().__init__(handler)
        parts = make_multipart_parts_from_request_files(data)
        self._d: Mapping[str, MultipartFormData.Field] = {p.name: p for p in parts}

    async def _send(self, p: SendParams) -> Exchange:
        pld = p.requisition.payload
        if not isinstance(pld, MultipartFormData):
            raise RuntimeError('payload is not multipart form data')
        parts = pld.parts
        if not isinstance(parts, MutableSequence):
            raise RuntimeError('payload is non-mutable')
        d = {p.name: p for p in parts}
        d.update({**self._d, **d})
        parts.clear()
        parts.extend(d.values())
        return await super()._send(p)
