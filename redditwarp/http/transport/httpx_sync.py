
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping
if TYPE_CHECKING:
    from ..request import Request

import sys

import httpx
import httpcore

from ..transporter_info import TransporterInfo
from ..base_session_sync import BaseSession
from .. import exceptions
from .. import payload
from ..response import Response

_PAYLOAD_DISPATCH_TABLE: Mapping = {
    type(None): lambda y: {},
    payload.Raw: lambda y: {'data': y.data},
    payload.FormData: lambda y: {'data': y.data},
    payload.MultiPart: lambda y: {'files': y.data},
    payload.Text: lambda y: {'data': y.text},
    payload.JSON: lambda y: {'json': y.json},
}

def _request_kwargs(r: Request) -> Mapping[str, object]:
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
info = TransporterInfo(name, version, sys.modules[__name__])


class Session(BaseSession):
    TRANSPORTER = info
    TIMEOUT = 5

    def __init__(self,
        client: httpx.Client,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(params=params, headers=headers)
        self.client = client

    def request(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
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
    params: Optional[Mapping[str, str]] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> Session:
    limits = httpx.PoolLimits(max_connections=20)
    cl = httpx.Client(pool_limits=limits)
    return Session(cl, params=params, headers=headers)
