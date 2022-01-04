
from __future__ import annotations
from typing import Optional, Sequence, cast, Any

import asyncio

# https://pypi.org/project/websockets/
import websockets  # type: ignore[import]
import websockets.legacy.client  # type: ignore[import]
import websockets.typing  # type: ignore[import]
import websockets.connection

from .._ASYNC_ import register
from ...websocket_connection_ASYNC import PulsePartiallyImplementedWebSocketConnection
from ... import exceptions
from ...events import Frame
from ...const import Side


def _get_necessary_timeout(timeout: float = -2) -> Optional[float]:
    t: Optional[float] = timeout
    if timeout == -2:
        t = PulsePartiallyImplementedWebSocketConnection.DEFAULT_WAITTIME
    elif timeout == -1:
        t = None
    elif timeout < 0:
        raise ValueError(f'invalid timeout value: {timeout}')
    return t


class WebSocketClient(PulsePartiallyImplementedWebSocketConnection):
    side: int = Side.CLIENT

    def __init__(self, ws: websockets.legacy.client.WebSocketClientProtocol):
        super().__init__()
        self.ws: websockets.legacy.client.WebSocketClientProtocol = ws

    async def _send_frame_impl(self, m: Frame) -> None:
        try:
            await self.ws.write_frame(opcode=m.opcode, data=m.data, fin=m.fin)
        except Exception as cause:
            raise exceptions.TransportError from cause

    async def _load_next_frame(self, *, timeout: float = -2) -> Frame:
        t = _get_necessary_timeout(timeout)
        try:
            frm = await asyncio.wait_for(self.ws.read_frame(self.ws.max_size), t)
        except asyncio.TimeoutError as cause:
           raise exceptions.TimeoutException from cause
        #except websocket.WebSocketConnectionClosedException as cause:
        #    raise exceptions.ConnectionClosedException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        return Frame(
            opcode=frm.opcode,
            fin=frm.fin,
            data=frm.data,
        )

    async def shutdown(self) -> None:
        await super().close()
        try:
            await asyncio.wait_for(self.ws.transfer_data_task, self.ws.close_timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass

        await asyncio.shield(self.ws.close_connection_task)


async def connect(url: str, *, subprotocols: Sequence[str] = (), timeout: float = -2) -> WebSocketClient:
    t = _get_necessary_timeout(timeout)

    class MyWebSocketClientProtocol(websockets.legacy.client.WebSocketClientProtocol):
        def connection_open(self) -> None:
            self.state = websockets.connection.State.OPEN
            # self.transfer_data_task = self.loop.create_task(self.transfer_data())
            self.keepalive_ping_task = self.loop.create_task(self.keepalive_ping())
            self.close_connection_task = self.loop.create_task(self.close_connection())

    subp = cast(Optional[Sequence[websockets.typing.Subprotocol]], subprotocols if subprotocols else None)
    klass: Any = MyWebSocketClientProtocol
    coro = websockets.legacy.client.connect(url, create_protocol=klass, subprotocols=subp)
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
