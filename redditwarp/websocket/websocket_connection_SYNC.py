
from typing import Union, Iterator, Optional, MutableSequence

from abc import ABC, abstractmethod
import time

from .const import Opcode, ConnectionState, Side
from . import exceptions
from . import events
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

    def __iter__(self) -> Iterator[Event]:
        yield from self.cycle()

    def set_state(self, state: ConnectionState) -> None:
        self.state = state

    @abstractmethod
    def send_frame(self, m: Frame) -> None:
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')

    def send_text(self, data: str) -> None:
        self.send_frame(Frame.make(Opcode.TEXT, data.encode()))

    def send_bytes(self, data: bytes) -> None:
        self.send_frame(Frame.make(Opcode.BINARY, data))

    def send(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            self.send_text(data)
        else:
            self.send_bytes(data)

    @abstractmethod
    def _load_next_frame(self, *, timeout: float = -2) -> Frame:
        raise NotImplementedError

    def _process_ping(self, m: Frame) -> Iterator[Event]:
        if self.state not in {ConnectionState.CLOSE_RECEIVED, ConnectionState.CLOSED}:
            pong = Frame.make(Opcode.PONG, m.data)
            self.send_frame(pong)
        yield m

    def _process_close(self, m: Frame) -> Iterator[Event]:
        self.set_state(ConnectionState.CLOSE_RECEIVED)
        self.close_code, self.close_reason = parse_close(m.data)

        if self.state == ConnectionState.OPEN:
            close = Frame.make(Opcode.CLOSE, m.data)
            self.send_frame(close)
        yield m

    def _process_data_frame(self, m: Frame) -> Iterator[Event]:
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
    def _process_frame(self, m: Frame) -> Iterator[Event]:
        if m.opcode == Opcode.PING:
            yield from self._process_ping(m)
        elif m.opcode == Opcode.CLOSE:
            yield from self._process_close(m)
        elif m.opcode in {Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY}:
            yield from self._process_data_frame(m)

    def pulse(self, *, timeout: float = -2) -> Iterator[Event]:
        """Process one frame’s worth of incoming data and possibly generate events for it."""
        frame = self._load_next_frame(timeout=timeout)
        yield from self._process_frame(frame)

    def cycle(self, t: Optional[float] = None) -> Iterator[Event]:
        """Yield events from `self.pulse()` over `t` seconds."""
        if t is None:
            while True:
                yield from self.pulse(timeout=-1)

        else:
            tv = t
            tn = time.monotonic()
            while tv > 0:
                try:
                    yield from self.pulse(timeout=tv)
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

    def receive(self, *, timeout: float = -2) -> Message:
        t = self._get_cycle_value(timeout)
        for event in self.cycle(t):
            if isinstance(event, Message):
                return event
        raise exceptions.TimeoutError

    def recv_bytes(self, *, timeout: float = -2) -> bytes:
        """Receive the next message. If it's a BytesMessage then return its payload,
        otherwise raise an MessageTypeMismatchException exception."""
        event = self.receive(timeout=timeout)
        if isinstance(event, BytesMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('string message received')

    def recv_text(self, *, timeout: float = -2) -> str:
        """Receive the next message. If it's a TextMessage then return its payload,
        otherwise raise an MessageTypeMismatchException exception."""
        event = self.receive(timeout=timeout)
        if isinstance(event, TextMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('bytes message received')

    def _send_close(self, code: Optional[int] = 1000, reason: str = '') -> None:
        data = b''
        if code is not None:
            data = serialize_close(code, reason)

        close = Frame.make(Opcode.CLOSE, data)
        self.send_frame(close)

    @abstractmethod
    def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None and reason:
            raise ValueError('cannot send a reason without a code')

        self._send_close(code, reason)

        self.set_state(ConnectionState.CLOSE_SENT)

        try:
            t = self._get_cycle_value(waitfor)
        except ValueError:
            raise ValueError(f'invalid waitfor value: {waitfor}') from None

        for event in self.cycle(t):
            if isinstance(event, Frame):
                if event.opcode == Opcode.CLOSE:
                    break

        self.shutdown()

    @abstractmethod
    def shutdown(self) -> None:
        if self.close_code < 0:
            self.close_code = 1006

        self.set_state(ConnectionState.CLOSED)
