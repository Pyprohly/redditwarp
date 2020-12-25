
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Any, List
if TYPE_CHECKING:
    from ..request import Request
    from ..payload import Payload

import httpx  # type: ignore[import]
import httpcore  # type: ignore[import]

from ..transporter_info import TransporterInfo
from ..base_session_ASYNC import BaseSession
from .. import exceptions
from .. import payload
from ..response import Response
from .ASYNC import register

def _multipart_payload_dispatch(y: Payload) -> Mapping[str, object]:
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

    destructured_file_payloads = {
        p.name: (
            (p.filename, p.file)
            if p.content_type == '.' else
            (p.filename, p.file, p.content_type)
        )
        for p in file_payloads
    }

    return {
        'data': {p.name: p.value for p in text_payloads},
        'files': destructured_file_payloads,
    }

_PAYLOAD_DISPATCH_TABLE: Mapping[Any, Any] = {
    type(None): lambda y: {},
    payload.Bytes: lambda y: {'data': y.data},
    payload.FormData: lambda y: {'data': y.data},
    payload.Multipart: _multipart_payload_dispatch,
    payload.Text: lambda y: {'data': y.text},
    payload.JSON: lambda y: {'json': y.json},
}

def _request_kwargs(r: Request) -> Mapping[str, object]:
    for v in r.params.values():
        if v is None:
            msg = f'valueless URL params is not supported by this HTTP transport library ({info.name}); the params mapping cannot contain None'
            raise RuntimeError(msg)

    kwargs: MutableMapping[str, object] = {
        'method': r.verb,
        'url': r.uri,
        'params': r.params,
        'headers': r.headers,
    }
    d = _PAYLOAD_DISPATCH_TABLE[type(r.payload)](r.payload)
    kwargs.update(d)
    return kwargs


name = httpx.__name__
version = httpx.__version__
spec = __spec__  # type: ignore[name-defined]
info = TransporterInfo(name, version, spec)


class Session(BaseSession):
    TRANSPORTER_INFO = info
    TIMEOUT = 5

    def __init__(self,
        client: httpx.AsyncClient,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(params=params, headers=headers)
        self.client = client

    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        self._prepare_request(request)

        t: Optional[float] = timeout
        if timeout < 0:
            t = self.TIMEOUT
        elif timeout == 0:
            t = None

        kwargs: MutableMapping[str, object] = {'timeout': t}
        kwargs.update(_request_kwargs(request))

        try:
            resp = await self.client.request(**kwargs)
        except httpcore.TimeoutException as e:
            raise exceptions.TimeoutError from e
        except Exception as e:
            raise exceptions.TransportError from e

        return Response(
            status=resp.status_code,
            headers=resp.headers,
            data=resp.content,
            request=request,
            underlying_object=resp,
        )

    async def close(self) -> None:
        await self.client.aclose()


def new_session(*,
    params: Optional[Mapping[str, Optional[str]]] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> Session:
    limits = httpx.Limits(max_connections=20)
    cl = httpx.AsyncClient(pool_limits=limits)
    return Session(cl, params=params, headers=headers)

register(name, info, new_session)
