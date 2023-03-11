
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Mapping
if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from ...events import Frame

import asyncio

import aiohttp  # type: ignore[import]

from ..reg_ASYNC import register
from ...websocket_ASYNC import PartiallyImplementedWebSocket, DEFAULT_WAITTIME
from ... import exceptions
from ... import events
from ...const import Side, ConnectionState

class WebSocketClient(PartiallyImplementedWebSocket):
    SIDE: int = Side.CLIENT

    def __init__(self, ws: aiohttp.ClientWebSocketResponse, session: aiohttp.ClientSession) -> None:
        super().__init__()
        self.ws: aiohttp.ClientWebSocketResponse = ws
        ("")
        self.session: aiohttp.ClientSession = session
        ("")

    async def send_frame(self, m: Frame) -> None:
        raise RuntimeError('sending raw frames is not supported by aiohttp')

    async def send_text(self, data: str) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name!r} state')

        try:
            await self.ws.send_str(data)
        except Exception as cause:
            raise exceptions.TransportError from cause

    async def send_bytes(self, data: bytes) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name!r} state')

        try:
            await self.ws.send_bytes(data)
        except Exception as cause:
            raise exceptions.TransportError from cause

    async def _pulse_impl(self, *, timeout: float = -2) -> AsyncIterator[object]:
        t: Optional[float] = timeout
        if timeout == -2:
            t = self.default_waittime
        elif timeout == -1:
            t = None
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {t}')

        try:
            wsm = await self.ws.receive(timeout=t)
        except asyncio.TimeoutError as cause:
            raise exceptions.TimeoutException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        if wsm.type == aiohttp.WSMsgType.TEXT:
            yield events.TextMessage(wsm.data)
        elif wsm.type == aiohttp.WSMsgType.BINARY:
            yield events.BytesMessage(wsm.data)
        elif wsm.type == aiohttp.WSMsgType.CLOSING:
            self.state = ConnectionState.CLOSING
        elif wsm.type == aiohttp.WSMsgType.CLOSED:
            close_code = self.ws.close_code
            if not close_code:
                raise Exception('assertion')
            self.close_code: int = close_code
            self.state = ConnectionState.CLOSED
            yield events.ConnectionClosed()
        elif wsm.type == aiohttp.WSMsgType.ERROR:
            raise exceptions.TransportError from wsm.data

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None:
            raise RuntimeError('must specify a close code with aiohttp library websockets')

        t: Optional[float] = waitfor
        if waitfor == -2:
            t = self.default_waittime
        elif waitfor == -1:
            t = None
        elif waitfor < 0:
            raise ValueError(f'invalid waitfor value: {waitfor}')

        if self.state == ConnectionState.CLOSED:
            return
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'operation not permitted in {self.state.name!r} state')

        self.state: ConnectionState = ConnectionState.CLOSING

        coro = self.ws.close(code=code, message=reason.encode())
        try:
            await asyncio.wait_for(coro, t)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            raise exceptions.TransportError from e

        if self.ws.close_code:
            self.close_code = self.ws.close_code

        if self.close_code < 0:
            self.close_code = 1006
        self.state = ConnectionState.CLOSED

        await self.session.close()


async def connect(
    url: str,
    *,
    subprotocols: Sequence[str] = (),
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = -2,
) -> WebSocketClient:
    t: Optional[float] = timeout
    if timeout == -2:
        t = DEFAULT_WAITTIME
    elif timeout == -1:
        t = None
    elif timeout < 0:
        raise ValueError(f'invalid timeout value: {timeout}')

    session = aiohttp.ClientSession()
    coro = session.ws_connect(
        url,
        headers=headers,
        protocols=subprotocols,
    )
    try:
        ws = await asyncio.wait_for(coro, t)
    except asyncio.TimeoutError:
        await session.close()
        raise exceptions.TimeoutException

    wsc = WebSocketClient(ws, session)
    wsc.subprotocol = ws.protocol or ''
    return wsc


name: str = aiohttp.__name__
version: str = aiohttp.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    connect=connect,
)
