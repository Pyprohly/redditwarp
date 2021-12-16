
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Iterable
if TYPE_CHECKING:
    from ..request import Request
    from ..response import Response

import httpx  # type: ignore[import]

from ._SYNC_ import register
from ..session_base_SYNC import SessionBase
from .. import exceptions
from .. import payload
from ..response import UResponse

def _generate_request_kwargs(r: Request, etv: float) -> Iterable[tuple[str, Any]]:
    timeout_obj = httpx.Timeout(etv, pool=20)
    if etv == -1:
        timeout_obj = httpx.Timeout(None, pool=20)
    yield ('timeout', timeout_obj)

    yield ('method', r.verb)
    yield ('url', r.uri)
    yield ('params', r.params)

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

    elif isinstance(pld, payload.TextData):
        pld.apply_content_type(headers)
        yield ('data', pld.data)

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
        httpx_client: httpx.Client,
    ) -> None:
        super().__init__()
        self.client: httpx.Client = httpx_client

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        etv = self._get_effective_timeout_value(timeout)
        kwargs = dict(_generate_request_kwargs(request, etv))
        try:
            response = self.client.request(**kwargs)
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

    def close(self) -> None:
        self.client.close()

def new_session() -> Session:
    cl = httpx.Client()
    return Session(cl)

name: str = httpx.__name__
version: str = httpx.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
