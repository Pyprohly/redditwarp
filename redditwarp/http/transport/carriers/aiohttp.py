
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Iterable, Optional
if TYPE_CHECKING:
    from ...request import Request
    from ...response import Response

import asyncio

import aiohttp  # type: ignore[import]

from ..reg_ASYNC import register
from ...session_base_ASYNC import SessionBase
from ... import exceptions
from ... import payload
from ...response import UResponse
from ...util.case_insensitive_dict import CaseInsensitiveDict

def _get_effective_timeout_value(timeouts: Iterable[float]) -> float:
    for tv in timeouts:
        if tv == -2:
            continue
        if 0 > tv != -1:
            raise ValueError('invalid timeout value: %s' % tv)
        return tv
    raise ValueError('a default timeout value could not be determined')

def _generate_request_kwargs(
    session: SessionBase,
    request: Request,
    *,
    timeout: float = -2,
    follow_redirects: Optional[bool] = None,
) -> Iterable[tuple[str, Any]]:
    r = request
    etv = _get_effective_timeout_value((timeout, session.timeout))

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

    yield ('method', r.verb)
    yield ('url', r.uri)
    yield ('params', r.params)

    yield ('allow_redirects', (session.follow_redirects if follow_redirects is None else follow_redirects))

    headers = dict(r.headers)
    pld = r.payload
    if pld is None:
        pass

    elif isinstance(pld, payload.Bytes):
        pld.apply_content_type(headers)
        yield ('data', pld.data)

    elif isinstance(pld, payload.Text):
        pld.apply_content_type(headers)
        yield ('data', pld.text.encode())

    elif isinstance(pld, payload.JSON):
        yield ('json', pld.json)

    elif isinstance(pld, payload.URLEncodedFormData):
        yield ('data', dict(pld.data))

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
            raise Exception('multipart without file fields not supported')

        formdata = aiohttp.FormData()
        for ty in text_plds:
            formdata.add_field(ty.name, ty.value)
        for fy in file_plds:
            formdata.add_field(fy.name, fy.file, filename=fy.filename, content_type=fy.content_type)

        yield ('data', formdata)

    else:
        raise Exception('unsupported payload type')

    yield ('headers', headers)


class Session(SessionBase):
    def __init__(self,
        aiohttp_client: aiohttp.ClientSession,
    ) -> None:
        super().__init__()
        self.session: aiohttp.ClientSession = aiohttp_client

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        kwargs = dict(_generate_request_kwargs(self, request,
                timeout=timeout, follow_redirects=follow_redirects))
        try:
            async with self.session.request(**kwargs) as response:
                content = await response.content.read()
        except asyncio.TimeoutError as cause:
            raise exceptions.TimeoutException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        aiohttp_headers: Any = response.headers
        headers = CaseInsensitiveDict(dict(aiohttp_headers))
        return UResponse(
            status=response.status,
            headers=headers,
            data=content,
            underlying_object=response,
        )

    async def close(self) -> None:
        await self.session.close()

def new_session() -> Session:
    connector = aiohttp.TCPConnector(limit=20)
    se = aiohttp.ClientSession(connector=connector)
    return Session(se)

name: str = aiohttp.__name__
version: str = aiohttp.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
