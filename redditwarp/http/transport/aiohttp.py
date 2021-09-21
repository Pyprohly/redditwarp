"""Transport adapter for aiohttp."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Iterable
if TYPE_CHECKING:
    from ..request import Request

import asyncio

import aiohttp  # type: ignore[import]

from .ASYNC import register
from ..session_base_ASYNC import SessionBase
from .. import exceptions
from .. import payload
from ..response import Response
from ..util.case_insensitive_dict import CaseInsensitiveDict

def _generate_request_kwargs(r: Request, etv: float) -> Iterable[tuple[str, Any]]:
    client_timeout = aiohttp.ClientTimeout(
        total=etv,
        connect=etv,
        sock_connect=etv,
        sock_read=etv,
    )
    if etv == -1:
        client_timeout = aiohttp.ClientTimeout(
            total=None,
            connect=None,
            sock_connect=None,
            sock_read=None,
        )
    yield ('timeout', client_timeout)

    for v in r.params.values():
        if v is None:
            msg = f'valueless URL query params are not supported by this HTTP transport library ({name})'
            raise RuntimeError(msg)

    yield ('method', r.verb)
    yield ('url', r.uri)
    yield ('params', r.params)
    yield ('headers', r.headers)

    pld = r.payload
    if isinstance(pld, payload.Bytes):
        yield ('data', pld.data)

    elif isinstance(pld, payload.Text):
        yield ('data', pld.text)

    elif isinstance(pld, payload.JSON):
        yield ('json', pld.json)

    elif isinstance(pld, payload.URLEncodedFormData):
        for v in pld.data.values():
            if v is None:
                msg = f'valueless URL-encoded form data parameters are not supported by this HTTP transport library ({name})'
                raise RuntimeError(msg)

        yield ('data', pld.data)

    elif isinstance(pld, payload.MultipartFormData):
        text_plds: list[payload.MultipartTextField] = []
        file_plds: list[payload.MultipartFileField] = []
        for part in pld.parts:
            if isinstance(part, payload.MultipartTextField):
                text_plds.append(part)
            elif isinstance(part, payload.MultipartFileField):
                file_plds.append(part)

        if not file_plds:
            # aiohttp won't send a multipart if no files
            raise NotImplementedError('multipart without file fields not supported')

        formdata = aiohttp.FormData()
        for ty in text_plds:
            formdata.add_field(ty.name, ty.value)
        for fy in file_plds:
            formdata.add_field(fy.name, fy.file, filename=fy.filename, content_type=fy.content_type)

        yield ('data', formdata)

    else:
        raise NotImplementedError('unsupported payload type')


class Session(SessionBase):
    def __init__(self,
        aiohttp_client: aiohttp.ClientSession,
    ) -> None:
        super().__init__()
        self.session = aiohttp_client

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        etv = self._get_effective_timeout_value(timeout)
        kwargs = dict(_generate_request_kwargs(request, etv))
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
