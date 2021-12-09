
from typing import Union, AsyncIterator, Optional, MutableSequence

import time

from .const import Opcode, ConnectionState, Side
from . import exceptions
from . import events
from .events import Event, Frame, Message, BytesMessage, TextMessage
from .utils import parse_close, serialize_close

class WebSocketConnection:
    DEFAULT_TIMEOUT: int = 4
    side: int = Side.NONE

    def __init__(self) -> None:
        self.default_timeout: float = self.DEFAULT_TIMEOUT
        self.state: ConnectionState = ConnectionState.OPEN
        self.close_code: int = -1
        self.close_reason: str = ''
        self.subprotocol: str = ''

    async def __aiter__(self) -> AsyncIterator[Event]:
        async for event in self.cycle():
            yield event

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

    async def cycle(self, t: float = -1) -> AsyncIterator[Event]:
        if t == -1:
            while True:
                async for event in self.pulse(timeout=-1):
                    yield event
                    if isinstance(event, events.ConnectionClosed):
                        return

        else:
            tv = t
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

    async def shutdown(self) -> None:
        if self.close_code < 0:
            self.close_code = 1006

        self.state = ConnectionState.CLOSED

    async def send_frame(self, m: Frame) -> None:
        raise NotImplementedError

    async def send_text(self, data: str) -> None:
        raise NotImplementedError

    async def send_bytes(self, data: bytes) -> None:
        raise NotImplementedError

    async def send(self, data: Union[str, bytes]) -> None:
        raise NotImplementedError

    async def pulse(self, *, timeout: float = -2) -> AsyncIterator[Event]:
        raise NotImplementedError
        yield

    async def receive(self, *, timeout: float = -2) -> Message:
        raise NotImplementedError

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        raise NotImplementedError


class PartiallyImplementedWebSocketConnection(WebSocketConnection):
    def __init__(self) -> None:
        super().__init__()
        self._accumulator: MutableSequence[Frame] = []

    async def send_frame(self, m: Frame) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')

    async def send_text(self, data: str) -> None:
        await self.send_frame(Frame.make(Opcode.TEXT, data.encode()))

    async def send_bytes(self, data: bytes) -> None:
        await self.send_frame(Frame.make(Opcode.BINARY, data))

    async def send(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            await self.send_text(data)
        else:
            await self.send_bytes(data)

    async def _process_ping_frame(self, m: Frame) -> AsyncIterator[Event]:
        if self.state not in {ConnectionState.CLOSE_RECEIVED, ConnectionState.CLOSED}:
            pong = Frame.make(Opcode.PONG, m.data)
            await self.send_frame(pong)
        yield m

    async def _process_close_frame(self, m: Frame) -> AsyncIterator[Event]:
        self.state = ConnectionState.CLOSE_RECEIVED
        self.close_code: int
        self.close_reason: str
        self.close_code, self.close_reason = parse_close(m.data)

        if self.state == ConnectionState.OPEN:
            close = Frame.make(Opcode.CLOSE, m.data)
            try:
                await self.send_frame(close)
            except exceptions.ConnectionClosedException:
                pass

        await self.shutdown()

        yield m
        yield events.ConnectionClosed()

    async def _process_data_frame(self, m: Frame) -> AsyncIterator[Event]:
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

    async def _process_frame(self, m: Frame) -> AsyncIterator[Event]:
        if m.opcode == Opcode.PING:
            async for event in self._process_ping_frame(m):
                yield event
        elif m.opcode == Opcode.CLOSE:
            async for event in self._process_close_frame(m):
                yield event
        elif m.opcode in {Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY}:
            async for event in self._process_data_frame(m):
                yield event

    async def _load_next_frame(self, *, timeout: float = -2) -> Frame:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')
        raise NotImplementedError

    async def pulse(self, *, timeout: float = -2) -> AsyncIterator[Event]:
        frame = await self._load_next_frame(timeout=timeout)
        async for event in self._process_frame(frame):
            yield event

    def _get_cycle_value_from_timeout(self, timeout: float = -2) -> float:
        t: float = timeout
        if timeout == -2:
            t = self.default_timeout
        elif timeout == -1:
            t = -1
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {timeout}')
        return t

    def _get_cycle_value_from_waitfor(self, waitfor: float = -2) -> float:
        try:
            t = self._get_cycle_value_from_timeout(waitfor)
        except ValueError:
            raise ValueError(f'invalid waitfor value: {waitfor}') from None
        return t

    async def receive(self, *, timeout: float = -2) -> Message:
        t = self._get_cycle_value_from_timeout(timeout)
        async for event in self.cycle(t):
            if isinstance(event, Message):
                return event
            elif isinstance(event, events.ConnectionClosed):
                raise exceptions.ConnectionClosedException()
        raise exceptions.TimeoutException

    async def _send_close_frame(self, code: Optional[int] = 1000, reason: str = '') -> None:
        data = b''
        if code is not None:
            data = serialize_close(code, reason)

        close = Frame.make(Opcode.CLOSE, data)
        await self.send_frame(close)

    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None and reason:
            raise ValueError('cannot send a reason without a code')

        t = self._get_cycle_value_from_waitfor(waitfor)

        if self.state != ConnectionState.OPEN:
            return

        await self._send_close_frame(code, reason)

        self.state: ConnectionState = ConnectionState.CLOSE_SENT

        async for event in self.cycle(t):
            if isinstance(event, Frame):
                if event.opcode == Opcode.CLOSE:
                    break

        await self.shutdown()
