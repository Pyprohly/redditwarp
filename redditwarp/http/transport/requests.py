"""Transport adapter for Requests."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping
if TYPE_CHECKING:
    from ..request import Request

import sys

import requests

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


name = requests.__name__
version = requests.__version__
info = TransporterInfo(name, version, sys.modules[__name__])


class Session(BaseSession):
    TRANSPORTER = info
    TIMEOUT = 5

    def __init__(self,
        session: requests.Session,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(params=params, headers=headers)
        self.session = session

    def send(self, request: Request, *, timeout: float = -1,
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
            resp = self.session.request(**kwargs)
        except requests.exceptions.ReadTimeout as e:
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
        self.session.close()


def new_session(*,
    params: Optional[Mapping[str, str]] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> Session:
    se = requests.Session()
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
    se.mount('https://', retry_adapter)
    return Session(se, params=params, headers=headers)
