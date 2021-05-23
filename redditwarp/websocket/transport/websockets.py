
###
'''
Does not work.

Not sure how to get websockets to provide raw frames.
Calling `websockets.WebSocketClientProtocol.read_data_frame()` always results in
a RuntimeError for some reason. Not sure where to get help for this.
'''
###
######################




from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, cast
if TYPE_CHECKING:
    from collections.abc import AsyncIterator

import asyncio
import time

# https://pypi.org/project/websockets/
import websockets  # type: ignore[import]
import websockets.legacy.client

from ..websocket_connection_ASYNC import WebSocketConnection
from .. import exceptions
from ..events import Event, Frame
from ..const import Opcode, Side, ConnectionState

class WebSocketClient(WebSocketConnection):
    side = Side.CLIENT

    def __init__(self, ws: websockets.legacy.client.WebSocketClientProtocol):
        super().__init__()
        self.ws = ws

    async def send_frame(self, m: Frame) -> None:
        await super().send_frame(m)
        try:
            await self.ws.write_frame(opcode=m.opcode, data=m.data, fin=m.fin)
        except Exception as e:
            raise exceptions.TransportError from e

    async def _load_next_frame(self, *, timeout: float = -2) -> Frame:
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
                    frm = await self.ws.read_data_frame(max_size=self.ws.max_size)
                except Exception as e:
                    raise exceptions.TransportError from e

                if frm is not None:
                    return Frame(
                        opcode=Opcode(frm.opcode),
                        fin=frm.fin,
                        data=frm.data,
                    )

        else:
            tv = t
            tn = time.monotonic()
            while tv > 0:
                coro = self.ws.read_data_frame(max_size=self.ws.max_size)
                try:
                    frm = await asyncio.wait_for(coro, tv)
                except asyncio.TimeoutError as e:
                    raise exceptions.TimeoutError from e
                except Exception as e:
                    raise exceptions.TransportError from e

                if frm is not None:
                    return Frame(
                        opcode=Opcode(frm.opcode),
                        fin=frm.fin,
                        data=frm.data,
                    )

                now = time.monotonic()
                tv -= now - tn
                tn = now

            raise exceptions.TimeoutError

    async def _process_frame(self, m: Frame) -> AsyncIterator[Event]:
        if m.opcode in {Opcode.PING, Opcode.PONG, Opcode.CLOSE}:
            raise RuntimeError(f"websocket's read_data_frame method doesn't return {Opcode(m.opcode).name !r} frames")
        async for event in super()._process_frame(m):
            yield event

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
        except Exception as e:
            raise exceptions.TransportError from e

        self.set_state(ConnectionState.CLOSE_SENT)

        await self.shutdown()

async def connect(url: str, *, subprotocols: Sequence[str] = ()) -> WebSocketClient:
    subp = cast(Optional[Sequence[websockets.typing.Subprotocol]], subprotocols)
    ws = await websockets.legacy.client.connect(url, subprotocols=subp)
    return WebSocketClient(ws)
