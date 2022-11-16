
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Iterable, Optional
if TYPE_CHECKING:
    from ...request import Request
    from ...response import Response

import httpx  # type: ignore[import]

from ..reg_ASYNC import register
from ...session_base_ASYNC import SessionBase
from ... import exceptions
from ... import payload
from ...response import UResponse

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

    timeout_obj = httpx.Timeout(etv, pool=20)
    if etv == -1:
        timeout_obj = httpx.Timeout(None, pool=20)
    yield ('timeout', timeout_obj)

    yield ('method', r.verb)
    yield ('url', r.uri)
    yield ('params', r.params)

    yield ('follow_redirects', (session.follow_redirects if follow_redirects is None else follow_redirects))

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
            # httpx won't send a multipart if no files
            raise Exception('multipart without file fields not supported')

        yield ('data', {ty.name: ty.value for ty in text_plds})
        yield ('files', {
            fy.name: (fy.filename, fy.file, fy.content_type)
            for fy in file_plds
        })

    else:
        raise Exception('unsupported payload type')

    yield ('headers', headers)


class Session(SessionBase):
    def __init__(self,
        httpx_client: httpx.AsyncClient,
    ) -> None:
        super().__init__()
        self.client: httpx.AsyncClient = httpx_client

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        kwargs = dict(_generate_request_kwargs(self, request,
                timeout=timeout, follow_redirects=follow_redirects))
        try:
            response = await self.client.request(**kwargs)
        except httpx.TimeoutException as cause:
            raise exceptions.TimeoutException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        return UResponse(
            status=response.status_code,
            headers=response.headers,
            data=response.content,
            underlying_object=response,
        )

    async def close(self) -> None:
        await self.client.aclose()

def new_session() -> Session:
    limits = httpx.Limits(max_connections=20)
    cl = httpx.AsyncClient(limits=limits)
    return Session(cl)

name: str = httpx.__name__
version: str = httpx.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
