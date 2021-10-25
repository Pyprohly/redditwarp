"""Transport adapter for Requests."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, Iterable
if TYPE_CHECKING:
    from ..request import Request
    from ..response import Response

import requests  # type: ignore[import]
import requests.adapters  # type: ignore[import]

from .SYNC import register
from ..session_base_SYNC import SessionBase
from .. import exceptions
from .. import payload
from ..response import UResponse

def _generate_request_kwargs(r: Request, etv: float) -> Iterable[tuple[str, Any]]:
    t: Optional[float] = etv
    if t == -1:
        t = None
    yield ('timeout', t)

    yield ('method', r.verb)
    yield ('url', r.uri)
    yield ('params', r.params)
    yield ('headers', r.headers)

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
            # requests won't send a multipart if no files
            raise Exception('multipart without file fields not supported')

        yield ('data', {ty.name: ty.value for ty in text_plds})
        yield ('files', {
            fy.name: (fy.filename, fy.file, fy.content_type)
            for fy in file_plds
        })

    else:
        raise Exception('unsupported payload type')


class Session(SessionBase):
    def __init__(self,
        requests_session: requests.Session,
    ) -> None:
        super().__init__()
        self.session: requests.Session = requests_session

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        etv = self._get_effective_timeout_value(timeout)
        kwargs = dict(_generate_request_kwargs(request, etv))
        try:
            response = self.session.request(**kwargs)
        except requests.exceptions.ReadTimeout as cause:
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
        self.session.close()

def new_session() -> Session:
    se = requests.Session()
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
    se.mount('https://', retry_adapter)
    return Session(se)

name: str = requests.__name__
version: str = requests.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
