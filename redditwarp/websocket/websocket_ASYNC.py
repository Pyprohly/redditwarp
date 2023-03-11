
from typing import Union, AsyncIterator, Optional, MutableSequence

import time

from .const import Opcode, ConnectionState, Side
from . import exceptions
from . import events
from .events import Frame, Message, BytesMessage, TextMessage
from .utils import parse_close, serialize_close


DEFAULT_WAITTIME: float = 10.


class WebSocket:
    SIDE: int = Side.NONE

    def __init__(self) -> None:
        self.default_waittime: float = DEFAULT_WAITTIME
        ("")
        self.state: ConnectionState = ConnectionState.OPEN
        ("")
        self.close_code: int = -1
        ("")
        self.close_reason: str = ''
        ("")
        self.subprotocol: str = ''
        ("")

    async def __aiter__(self) -> AsyncIterator[object]:
        async for event in self.cycle(-1):
            yield event

    async def send_frame(self, m: Frame) -> None:
        raise NotImplementedError

    async def send_text(self, data: str) -> None:
        await self.send_frame(Frame.make(Opcode.TEXT, data.encode()))

    async def send_bytes(self, data: bytes) -> None:
        await self.send_frame(Frame.make(Opcode.BINARY, data))

    async def send(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            await self.send_text(data)
        else:
            await self.send_bytes(data)

    async def pulse(self, *, timeout: float = -2) -> AsyncIterator[object]:
        raise NotImplementedError
        yield

    async def cycle(self, t: float = -1) -> AsyncIterator[object]:
        if t < 0:
            while True:
                async for event in self.pulse(timeout=-1):
                    yield event
                    if isinstance(event, events.ConnectionClosed):
                        return

        else:
            tv = t
            if tv == -2:
                tv = self.default_waittime
            tn = time.monotonic()
            while tv > 0:
                try:
                    async for event in self.pulse(timeout=tv):
                        yield event
                        if isinstance(event, events.ConnectionClosed):
                            return
                except exceptions.TimeoutException:
                    return

                now = time.monotonic()
                tv -= now - tn
                tn = now

    async def receive(self, *, timeout: float = -2) -> Message:
        async for event in self.cycle(timeout):
            if isinstance(event, Message):
                return event
            elif isinstance(event, events.ConnectionClosed):
                raise exceptions.ConnectionClosedException
        raise exceptions.TimeoutException

    async def recv_bytes(self, *, timeout: float = -2) -> bytes:
        event = await self.receive(timeout=timeout)
        if isinstance(event, BytesMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('string message received')

    async def recv(self, *, timeout: float = -2) -> bytes:
        return await self.recv_bytes(timeout=timeout)

    async def recv_text(self, *, timeout: float = -2) -> str:
        event = await self.receive(timeout=timeout)
        if isinstance(event, TextMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('bytes message received')

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        raise NotImplementedError


class PartiallyImplementedWebSocket(WebSocket):
    async def _send_frame_impl(self, m: Frame) -> None:
        pass

    async def send_frame(self, m: Frame) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        elif self.state == ConnectionState.CLOSING:
            if m.opcode != Opcode.CLOSE:
                raise exceptions.InvalidStateException('cannot send non-close frame in closing state')
        elif self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name!r} state')

        await self._send_frame_impl(m)

    async def _pulse_impl(self, *, timeout: float = -2) -> AsyncIterator[object]:
        return
        yield

    async def pulse(self, *, timeout: float = -2) -> AsyncIterator[object]:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state not in {ConnectionState.OPEN, ConnectionState.CLOSING}:
            raise exceptions.InvalidStateException(f'cannot ingest frame in {self.state.name!r} state')

        async for event in self._pulse_impl(timeout=timeout):
            yield event

    async def _send_close_frame_impl(self, code: Optional[int] = 1000, reason: str = '') -> None:
        data = b''
        if code is not None:
            data = serialize_close(code, reason)
        close = Frame.make(Opcode.CLOSE, data)
        await self.send_frame(close)

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None and reason:
            raise ValueError('cannot send a reason without a code')

        if self.state == ConnectionState.CLOSED:
            return
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'operation not permitted in {self.state.name!r} state')

        self.state = ConnectionState.CLOSING

        await self._send_close_frame_impl(code, reason)

        async for _ in self.cycle(waitfor):
            pass

        if self.close_code < 0:
            self.close_code = 1006
        self.state: ConnectionState = ConnectionState.CLOSED



class PulsePartiallyImplementedWebSocketConnection(PartiallyImplementedWebSocket):
    def __init__(self) -> None:
        super().__init__()
        self._accumulator: MutableSequence[Frame] = []

    async def _process_ping_frame(self, m: Frame) -> AsyncIterator[object]:
        if self.state not in {ConnectionState.CLOSING, ConnectionState.CLOSED}:
            pong = Frame.make(Opcode.PONG, m.data)
            await self.send_frame(pong)
        yield m

    async def _process_close_frame(self, m: Frame) -> AsyncIterator[object]:
        self.state: ConnectionState = ConnectionState.CLOSING
        self.close_code: int
        self.close_reason: str
        self.close_code, self.close_reason = parse_close(m.data)

        close = Frame.make(Opcode.CLOSE, m.data)
        try:
            await self.send_frame(close)
        except exceptions.ConnectionClosedException:
            pass

        yield m

        if self.close_code < 0:
            self.close_code = 1006
        self.state = ConnectionState.CLOSED
        yield events.ConnectionClosed()

    async def _process_data_frame(self, m: Frame) -> AsyncIterator[object]:
        yield m
        acc = self._accumulator
        acc.append(m)
        if m.fin:
            msg = b''.join(m.data for m in acc)

            if acc[0].opcode & Opcode.TEXT:
                yield TextMessage(msg.decode())
            else:
                yield BytesMessage(msg)

            acc.clear()

    async def _process_frame(self, m: Frame) -> AsyncIterator[object]:
        if m.opcode == Opcode.PING:
            async for event in self._process_ping_frame(m):
                yield event
        elif m.opcode == Opcode.CLOSE:
            async for event in self._process_close_frame(m):
                yield event
        elif m.opcode in {Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY}:
            async for event in self._process_data_frame(m):
                yield event

    async def _load_next_frame(self, *, timeout: float = -2) -> Optional[Frame]:
        raise NotImplementedError

    async def _pulse_impl(self, *, timeout: float = -2) -> AsyncIterator[object]:
        frame = await self._load_next_frame(timeout=timeout)
        if frame is None:
            if self.close_code < 0:
                self.close_code = 1006
            self.state = ConnectionState.CLOSED
            yield events.ConnectionClosed()
        else:
            async for event in self._process_frame(frame):
                yield event
