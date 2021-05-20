
from typing import Union, AsyncIterator, Optional, MutableSequence

from abc import ABC, abstractmethod
import time

from .const import Opcode, ConnectionState, Side
from . import exceptions
from .events import Event, Frame, Message, BytesMessage, TextMessage
from .util import parse_close, serialize_close

class WebSocketConnection(ABC):
    side = Side.NONE

    def __init__(self) -> None:
        self.default_timeout: float = 4
        self.state = ConnectionState.OPEN
        self.close_code = -1
        self.close_reason = ''
        self.subprotocol = ''
        self._accumulator: MutableSequence[Frame] = []

    async def __aiter__(self) -> AsyncIterator[Event]:
        async for event in self.cycle():
            yield event

    def set_state(self, state: ConnectionState) -> None:
        self.state = state

    @abstractmethod
    async def send_frame(self, m: Frame) -> None:
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

    @abstractmethod
    async def _load_next_frame(self, *, timeout: float = -2) -> Frame:
        raise NotImplementedError

    async def _process_ping(self, m: Frame) -> AsyncIterator[Event]:
        if self.state not in {ConnectionState.CLOSE_RECEIVED, ConnectionState.CLOSED}:
            pong = Frame.make(Opcode.PONG, m.data)
            await self.send_frame(pong)
        yield m

    async def _process_close(self, m: Frame) -> AsyncIterator[Event]:
        self.set_state(ConnectionState.CLOSE_RECEIVED)
        self.close_code, self.close_reason = parse_close(m.data)

        if self.state == ConnectionState.OPEN:
            close = Frame.make(Opcode.CLOSE, m.data)
            await self.send_frame(close)
        yield m

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

    @abstractmethod
    async def _process_frame(self, m: Frame) -> AsyncIterator[Event]:
        if m.opcode == Opcode.PING:
            async for event in self._process_ping(m):
                yield event
        elif m.opcode == Opcode.CLOSE:
            async for event in self._process_close(m):
                yield event
        elif m.opcode in {Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY}:
            async for event in self._process_data_frame(m):
                yield event

    async def pulse(self, *, timeout: float = -2) -> AsyncIterator[Event]:
        """Process one frame’s worth of incoming data and possibly generate events for it."""
        frame = await self._load_next_frame(timeout=timeout)
        async for event in self._process_frame(frame):
            yield event

    async def cycle(self, t: Optional[float] = None) -> AsyncIterator[Event]:
        """Yield events from `self.pulse()` over `t` seconds."""
        if t is None:
            while True:
                async for event in self.pulse(timeout=-1):
                    yield event

        else:
            tv = t
            tn = time.monotonic()
            while tv > 0:
                try:
                    async for event in self.pulse(timeout=tv):
                        yield event
                except exceptions.TimeoutError:
                    break

                now = time.monotonic()
                tv -= now - tn
                tn = now

    def _get_cycle_value(self, timeout: float = -2) -> Optional[float]:
        t: Optional[float] = timeout
        if timeout == -2:
            t = self.default_timeout
        elif timeout == -1:
            t = None
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {timeout}')
        return t

    async def receive(self, *, timeout: float = -2) -> Message:
        t = self._get_cycle_value(timeout)
        async for event in self.cycle(t):
            if isinstance(event, Message):
                return event
        raise exceptions.TimeoutError

    async def recv_bytes(self, *, timeout: float = -2) -> bytes:
        """Receive the next message. If it's a BytesMessage then return its payload,
        otherwise raise an MessageTypeMismatchException exception."""
        event = await self.receive(timeout=timeout)
        if isinstance(event, BytesMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('string message received')

    async def recv_text(self, *, timeout: float = -2) -> str:
        """Receive the next message. If it's a TextMessage then return its payload,
        otherwise raise an MessageTypeMismatchException exception."""
        event = await self.receive(timeout=timeout)
        if isinstance(event, TextMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('bytes message received')

    async def _send_close(self, code: Optional[int] = 1000, reason: str = '') -> None:
        data = b''
        if code is not None:
            data = serialize_close(code, reason)

        close = Frame.make(Opcode.CLOSE, data)
        await self.send_frame(close)

    @abstractmethod
    async def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None and reason:
            raise ValueError('cannot send a reason without a code')

        await self._send_close(code, reason)

        self.set_state(ConnectionState.CLOSE_SENT)

        try:
            t = self._get_cycle_value(waitfor)
        except ValueError:
            raise ValueError(f'invalid waitfor value: {waitfor}') from None

        async for event in self.cycle(t):
            if isinstance(event, Frame):
                if event.opcode == Opcode.CLOSE:
                    break

        await self.shutdown()

    @abstractmethod
    async def shutdown(self) -> None:
        if self.close_code < 0:
            self.close_code = 1006

        self.set_state(ConnectionState.CLOSED)
