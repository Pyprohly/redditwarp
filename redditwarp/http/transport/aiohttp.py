"""Transport adapter for aiohttp."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..request import Request

import asyncio
import aiohttp

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


name = 'aiohttp'
version_string = aiohttp.__version__


class Session(BaseSession):
    TIMEOUT = 8

    def __init__(self,
        session: aiohttp.ClientSession,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(params=params, headers=headers)
        self.session = session

    async def request(self, request: Request, *, timeout: Optional[float] = TIMEOUT,
            aux_info: Optional[Mapping] = None) -> Response:
        self._prepare_request(request)

        if timeout is None:
            timeout = self.TIMEOUT

        aiohttp_client_timeout_kwargs = {'total': 5*60, 'connect': timeout}

        if timeout < 0:
            aiohttp_client_timeout_kwargs.clear()

        r = request
        kwargs: Any = {
            'method': r.verb,
            'url': r.uri,
            'params': r.params,
            'headers': r.headers,
            'timeout': aiohttp.ClientTimeout(**aiohttp_client_timeout_kwargs),
        }
        kwargs_x = _PAYLOAD_DISPATCH_TABLE[type(r.payload)](r.payload)
        kwargs.update(kwargs_x)

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
            request=r,
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
