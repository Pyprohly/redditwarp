
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, cast
if TYPE_CHECKING:
    from collections.abc import AsyncIterator

import asyncio

# https://pypi.org/project/websockets/
import websockets  # type: ignore[import]
import websockets.legacy.client  # type: ignore[import]
import websockets.typing  # type: ignore[import]
import websockets.exceptions  # type: ignore[import]

from ..reg_ASYNC import register
from ...websocket_ASYNC import PartiallyImplementedWebSocket, DEFAULT_WAITTIME
from ... import exceptions
from ... import events
from ...events import Frame, TextMessage, BytesMessage
from ...const import Side, ConnectionState

class WebSocketClient(PartiallyImplementedWebSocket):
    SIDE: int = Side.CLIENT

    def __init__(self, ws: websockets.legacy.client.WebSocketClientProtocol) -> None:
        super().__init__()
        self.ws: websockets.legacy.client.WebSocketClientProtocol = ws

    async def _send_frame_impl(self, m: Frame) -> None:
        try:
            await self.ws.write_frame(opcode=m.opcode, data=m.data, fin=m.fin)
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
            data = await asyncio.wait_for(self.ws.recv(), t)
        except asyncio.TimeoutError as cause:
            raise exceptions.TimeoutException from cause
        except websockets.exceptions.ConnectionClosed as e:
            self.close_code: int = e.code
            self.close_reason: str = e.reason
            await self.shutdown()
            yield events.ConnectionClosed()
        except Exception as cause:
            raise exceptions.TransportError from cause
        else:
            if isinstance(data, str):
                yield TextMessage(data)
            else:
                yield BytesMessage(data)

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None:
            raise RuntimeError('must specify a close code with websockets library websockets')

        t: Optional[float] = waitfor
        if waitfor == -2:
            t = self.default_waittime
        elif waitfor == -1:
            t = None
        elif waitfor < 0:
            raise ValueError(f'invalid waitfor value: {waitfor}')

        if t is None:
            raise RuntimeError('the websockets library does not support infinite waitfor')

        if self.state == ConnectionState.CLOSED:
            return
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'operation not permitted in {self.state.name!r} state')

        self.state: ConnectionState = ConnectionState.CLOSING

        self.ws.close_timeout = t
        try:
            await self.ws.close(code, reason)
        except Exception as cause:
            raise exceptions.TransportError from cause

        await self.shutdown()


async def connect(url: str, *, subprotocols: Sequence[str] = (), timeout: float = -2) -> WebSocketClient:
    t: Optional[float] = timeout
    if timeout == -2:
        t = DEFAULT_WAITTIME
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
