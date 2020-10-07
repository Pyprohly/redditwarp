
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Any
if TYPE_CHECKING:
    from ..request import Request

import httpx  # type: ignore[import]
import httpcore  # type: ignore[import]

from ..transporter_info import TransporterInfo
from ..base_session_SYNC import BaseSession
from .. import exceptions
from .. import payload
from ..response import Response
from .SYNC import register

_PAYLOAD_DISPATCH_TABLE: Mapping[Any, Any] = {
    type(None): lambda y: {},
    payload.Raw: lambda y: {'data': y.data},
    payload.FormData: lambda y: {'data': y.data},
    payload.MultiPart: lambda y: {'files': y.data},
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
        client: httpx.Client,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(params=params, headers=headers)
        self.client = client

    def send(self, request: Request, *, timeout: float = -1,
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
            resp = self.client.request(**kwargs)
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

    def close(self) -> None:
        self.client.close()


def new_session(*,
    params: Optional[Mapping[str, Optional[str]]] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> Session:
    limits = httpx.Limits(max_connections=20)
    cl = httpx.Client(pool_limits=limits)
    return Session(cl, params=params, headers=headers)

register(name, info, new_session)
