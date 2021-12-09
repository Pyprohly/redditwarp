
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, cast, Union
if TYPE_CHECKING:
    from collections.abc import AsyncIterator

import asyncio
import time

# https://pypi.org/project/websockets/
import websockets  # type: ignore[import]
import websockets.legacy.client  # type: ignore[import]
import websockets.typing  # type: ignore[import]
import websockets.exceptions

from .ASYNC import register
from ..websocket_connection_ASYNC import WebSocketConnection
from .. import exceptions
from .. import events
from ..events import Event, Frame, Message, TextMessage, BytesMessage
from ..const import Opcode, Side, ConnectionState

class WebSocketClient(WebSocketConnection):
    side: int = Side.CLIENT

    def __init__(self, ws: websockets.legacy.client.WebSocketClientProtocol):
        super().__init__()
        self.ws: websockets.legacy.client.WebSocketClientProtocol = ws

    async def send_frame(self, m: Frame) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')

        try:
            await self.ws.write_frame(opcode=m.opcode, data=m.data, fin=m.fin)
        except Exception as e:
            raise exceptions.TransportError from e

    async def send_text(self, data: str) -> None:
        await self.send_frame(Frame.make(Opcode.TEXT, data.encode()))

    async def send_bytes(self, data: bytes) -> None:
        await self.send_frame(Frame.make(Opcode.BINARY, data))

    async def send(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            await self.send_text(data)
        else:
            await self.send_bytes(data)

    async def pulse(self, *, timeout: float = -2) -> AsyncIterator[Event]:
        was_closed = self.state == ConnectionState.CLOSED
        try:
            yield await self.receive(timeout=timeout)
        except exceptions.ConnectionClosedException:
            if was_closed:
                raise
            yield events.ConnectionClosed()

    async def receive(self, *, timeout: float = -2) -> Message:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot receive frames in {self.state.name} state')

        t: Optional[float] = timeout
        if timeout == -2:
            t = self.default_timeout
        elif timeout == -1:
            t = None
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {t}')

        if t is None:
            while True:
                try:
                    data = await self.ws.recv()
                except websockets.exceptions.ConnectionClosedOK as e:
                    self.close_code = e.code
                    self.close_reason = e.reason
                    await self.shutdown()
                    raise exceptions.ConnectionClosedException
                except Exception as cause:
                    raise exceptions.TransportError from cause

                if isinstance(data, str):
                    return TextMessage(data)
                else:
                    return BytesMessage(data)

        else:
            tv = t
            tn = time.monotonic()
            while tv > 0:
                try:
                    data = await asyncio.wait_for(self.ws.recv(), t)
                except asyncio.TimeoutError as cause:
                    raise exceptions.TimeoutException from cause
                except websockets.exceptions.ConnectionClosedOK as e:
                    self.close_code: int = e.code
                    self.close_reason: str = e.reason
                    await self.shutdown()
                    raise exceptions.ConnectionClosedException
                except Exception as cause:
                    raise exceptions.TransportError from cause

                now = time.monotonic()
                tv -= now - tn
                tn = now

                if isinstance(data, str):
                    return TextMessage(data)
                else:
                    return BytesMessage(data)

            raise exceptions.TimeoutException

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None:
            raise RuntimeError('the websockets library does not support closing without a code')

        t: Optional[float] = waitfor
        if waitfor == -2:
            t = self.default_timeout
        elif waitfor == -1:
            t = None
        elif waitfor < 0:
            raise ValueError(f'invalid waitfor value: {waitfor}')

        if t is None:
            raise RuntimeError('the websockets library does not support infinite waitfor')

        self.ws.close_timeout = t
        try:
            await self.ws.close(code, reason)
        except Exception as cause:
            raise exceptions.TransportError from cause

        self.state: ConnectionState = ConnectionState.CLOSE_SENT

        await self.shutdown()


async def connect(url: str, *, subprotocols: Sequence[str] = (), timeout: float = -2) -> WebSocketClient:
    t: Optional[float] = timeout
    if timeout == -2:
        t = WebSocketConnection.DEFAULT_TIMEOUT
    elif timeout == -1:
        t = None
    elif timeout < 0:
        raise ValueError(f'invalid timeout value: {timeout}')

    subp = cast(Optional[Sequence[websockets.typing.Subprotocol]], subprotocols if subprotocols else None)
    coro = websockets.legacy.client.connect(url, subprotocols=subp)
    try:
        ws = await asyncio.wait_for(coro, t)
    except asyncio.TimeoutError as cause:
        raise exceptions.TimeoutException from cause
    except Exception as cause:
        raise exceptions.TransportError from cause

    return WebSocketClient(ws)


name: str = websockets.__name__
version: str = websockets.__version__  # type: ignore[attr-defined]
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    connect=connect,
)
