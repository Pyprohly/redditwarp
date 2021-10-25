
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Union
if TYPE_CHECKING:
    from collections.abc import AsyncIterator

import asyncio
import time

import aiohttp  # type: ignore[import]

from .ASYNC import register
from ..websocket_connection_ASYNC import WebSocketConnection
from .. import exceptions
from ..events import Event, Frame, Message, TextMessage, BytesMessage
from ..const import Side, ConnectionState

class WebSocketClient(WebSocketConnection):
    side: int = Side.CLIENT

    def __init__(self, ws: aiohttp.ClientWebSocketResponse, session: aiohttp.ClientSession):
        super().__init__()
        self.ws: aiohttp.ClientWebSocketResponse = ws
        self.session: aiohttp.ClientSession = session

    async def send_frame(self, m: Frame) -> None:
        raise RuntimeError('operation not supported')

    async def send_text(self, data: str) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')

        try:
            await self.ws.send_str(data)
        except Exception as e:
            raise exceptions.TransportError from e

    async def send_bytes(self, data: bytes) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')

        try:
            await self.ws.send_bytes(data)
        except Exception as e:
            raise exceptions.TransportError from e

    async def send(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            await self.send_text(data)
        else:
            await self.send_bytes(data)

    async def pulse(self, *, timeout: float = -2) -> AsyncIterator[Event]:
        raise RuntimeError('operation not supported')
        yield

    async def receive(self, *, timeout: float = -2) -> Message:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')

        t: Optional[float] = timeout
        if timeout == -2:
            t = self.default_timeout
        elif timeout == -1:
            t = None
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {t}')

        def _accept(wsm: aiohttp.WSMessage) -> Optional[Message]:
            if wsm.type == aiohttp.WSMsgType.TEXT:
                return TextMessage(wsm.data)
            elif wsm.type == aiohttp.WSMsgType.BINARY:
                return BytesMessage(wsm.data)
            elif wsm.type in {aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING}:
                raise exceptions.ConnectionClosedException
            elif wsm.type == aiohttp.WSMsgType.ERROR:
                raise exceptions.TransportError
            return None

        if t is None:
            while True:
                try:
                    wsm = await self.ws.receive(timeout=t)
                except Exception as e:
                    raise exceptions.TransportError from e

                if (v := _accept(wsm)) is not None:
                    return v

        else:
            tv = t
            tn = time.monotonic()
            while tv > 0:
                try:
                    wsm = await self.ws.receive(timeout=t)
                except Exception as e:
                    raise exceptions.TransportError from e

                if (v := _accept(wsm)) is not None:
                    return v

                now = time.monotonic()
                tv -= now - tn
                tn = now

            raise exceptions.TimeoutException

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None:
            raise RuntimeError('code=None not supported with aiohttp websockets')

        t: Optional[float] = waitfor
        if waitfor == -2:
            t = self.default_timeout
        elif waitfor == -1:
            t = None
        elif waitfor < 0:
            raise ValueError(f'invalid waitfor value: {t}')

        coro = self.ws.close(code=code, message=reason.encode())
        try:
            await asyncio.wait_for(coro, t)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            raise exceptions.TransportError from e

        await self.session.close()

        if self.ws.close_code:
            self.close_code: int = self.ws.close_code

        await self.shutdown()


async def connect(url: str, *, subprotocols: Sequence[str] = (), timeout: float = -2) -> WebSocketClient:
    t: Optional[float] = timeout
    if timeout == -2:
        t = WebSocketConnection.DEFAULT_TIMEOUT
    elif timeout == -1:
        t = None
    elif timeout < 0:
        raise ValueError(f'invalid timeout value: {timeout}')

    session = aiohttp.ClientSession()
    coro = session.ws_connect(url)
    try:
        ws = await asyncio.wait_for(coro, t)
    except asyncio.TimeoutError:
        await session.close()
        raise exceptions.TimeoutException

    return WebSocketClient(ws, session)


name: str = aiohttp.__name__
version: str = aiohttp.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    connect=connect,
)
