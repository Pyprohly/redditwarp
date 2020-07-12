"""Transport adapter for aiohttp."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping
if TYPE_CHECKING:
    from ..request import Request

import sys
import asyncio

import aiohttp

from ..transporter_info import TransporterInfo
from ..base_session_async import BaseSession
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


name = aiohttp.__name__
version = aiohttp.__version__
info = TransporterInfo(name, version, sys.modules[__name__])


class Session(BaseSession):
    TRANSPORTER = info
    TIMEOUT = 5

    def __init__(self,
        session: aiohttp.ClientSession,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(params=params, headers=headers)
        self.session = session

    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        self._prepare_request(request)

        if timeout < 0:
            timeout = self.TIMEOUT
        aiohttp_client_timeout_kwargs = {
            'total': 5*60,
            'connect': timeout,
            'sock_connect': timeout,
            'sock_read': timeout,
        }
        if timeout == 0:
            aiohttp_client_timeout_kwargs.clear()

        kwargs: MutableMapping[str, object] = {
            'timeout': aiohttp.ClientTimeout(**aiohttp_client_timeout_kwargs),
        }
        kwargs.update(_request_kwargs(request))

        try:
            async with self.session.request(**kwargs) as resp:
                content = await resp.content.read()
        except asyncio.TimeoutError as e:
            raise exceptions.TimeoutError from e
        except Exception as e:
            raise exceptions.TransportError from e

        return Response(
            status=resp.status,
            headers=resp.headers,
            data=content,
            request=request,
            underlying_object=resp,
        )

    async def close(self) -> None:
        await self.session.close()


def new_session(*,
    params: Optional[Mapping[str, str]] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> Session:
    connector = aiohttp.TCPConnector(limit=20)
    se = aiohttp.ClientSession(connector=connector)
    return Session(se, params=params, headers=headers)
