"""Transport adapter for aiohttp."""

from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, MutableMapping, Any, List
if TYPE_CHECKING:
    from ..request import Request
    from ..payload import Payload

import asyncio

import aiohttp  # type: ignore[import]

from .ASYNC import register
from ..session_base_ASYNC import SessionBase
from .. import exceptions
from .. import payload
from ..response import Response
from ..util.case_insensitive_dict import CaseInsensitiveDict

def _multipart_payload_dispatch(y: Payload) -> Mapping[str, Any]:
    if not isinstance(y, payload.Multipart):
        raise Exception

    text_payloads: List[payload.MultipartTextData] = []
    file_payloads: List[payload.MultipartFileData] = []
    for part in y.parts:
        if part.headers:
            raise NotImplementedError('multipart body part additional headers not implemented')

        sub_payload = part.payload

        if isinstance(sub_payload, payload.MultipartTextData):
            text_payloads.append(sub_payload)
        elif isinstance(sub_payload, payload.MultipartFileData):
            file_payloads.append(sub_payload)
        else:
            raise NotImplementedError('mixed multipart not implemented')

    if not file_payloads:
        raise NotImplementedError('multipart without file fields not supported')

    formdata = aiohttp.FormData()
    for ty in text_payloads:
        formdata.add_field(ty.name, ty.value)
    for fy in file_payloads:
        ct = fy.content_type
        if ct is None:
            raise NotImplementedError('multipart file none content type not supported')
        formdata.add_field(fy.name, fy.file, filename=fy.filename,
                content_type=(None if ct == '.' else ct))

    return {'data': formdata}

def _request_kwargs(r: Request) -> Mapping[str, Any]:
    for v in r.params.values():
        if v is None:
            msg = f'valueless URL params is not supported by this HTTP transport library ({name}); the params mapping cannot contain None'
            raise RuntimeError(msg)

    kwargs: MutableMapping[str, Any] = {
        'method': r.verb,
        'url': r.uri,
        'params': r.params,
        'headers': r.headers,
    }
    d = _PAYLOAD_DISPATCH_TABLE[type(r.payload)](r.payload)
    kwargs.update(d)
    return kwargs

_PAYLOAD_DISPATCH_TABLE: Mapping[Any, Any] = {
    type(None): lambda y: {},
    payload.Bytes: lambda y: {'data': y.data},
    payload.FormData: lambda y: {'data': y.data},
    payload.Multipart: _multipart_payload_dispatch,
    payload.Text: lambda y: {'data': y.text},
    payload.JSON: lambda y: {'json': y.json},
}


class Session(SessionBase):
    def __init__(self,
        aiohttp_client: aiohttp.ClientSession,
    ) -> None:
        super().__init__()
        self.session = aiohttp_client

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        etv = self._get_effective_timeout_value(timeout)
        client_timeout = aiohttp.ClientTimeout(
            total=etv,
            connect=etv,
            sock_connect=etv,
            sock_read=etv,
        )
        if timeout == -1:
            client_timeout = aiohttp.ClientTimeout(
                total=None,
                connect=None,
                sock_connect=None,
                sock_read=None,
            )

        kwargs: MutableMapping[str, Any] = {'timeout': client_timeout}
        kwargs.update(_request_kwargs(request))

        try:
            async with self.session.request(**kwargs) as response:
                content = await response.content.read()
        except asyncio.TimeoutError as e:
            raise exceptions.TimeoutException from e
        except Exception as e:
            raise exceptions.TransportError from e

        aiohttp_headers: Any = response.headers
        headers = CaseInsensitiveDict(dict(aiohttp_headers))
        return Response(
            status=response.status,
            headers=headers,
            data=content,
            request=request,
            underlying_object=response,
        )

    async def close(self) -> None:
        await self.session.close()

def new_session() -> Session:
    connector = aiohttp.TCPConnector(limit=20)
    se = aiohttp.ClientSession(connector=connector)
    return Session(se)

name = aiohttp.__name__
version = aiohttp.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
