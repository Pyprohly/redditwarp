
from typing import Union, Iterator, Optional, MutableSequence

from abc import ABC, abstractmethod
import time

from .const import Opcode, ConnectionState, Side
from . import exceptions
from . import events
from .events import Event, Frame, Message, BytesMessage, TextMessage
from .util import parse_close, serialize_close

class WebSocketConnectionAbstractBase(ABC):
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
            raise exceptions.InvalidState(f'cannot send frame in {self.state.name} state')

    def send_text(self, data: str) -> None:
        self.send_frame(
                Frame.make(Opcode.TEXT, data.encode()))

    def send_bytes(self, data: bytes) -> None:
        self.send_frame(
                Frame.make(Opcode.BINARY, data))

    def send(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            self.send_text(data)
        else:
            self.send_bytes(data)

    @abstractmethod
    def _load_next_frame(self, *, timeout: float = 0) -> Frame:
        raise NotImplementedError

    def _process_ping(self, m: Frame) -> None:
        if self.state not in {ConnectionState.CLOSE_RECEIVED, ConnectionState.CLOSED}:
            pong = Frame.make(Opcode.PONG, m.data)
            self.send_frame(pong)

    def _process_close(self, m: Frame) -> None:
        self.set_state(ConnectionState.CLOSE_RECEIVED)
        self.close_code, self.close_reason = parse_close(event.data)

        if self.state == ConnectionState.OPEN:
            close = Frame.make(Opcode.CLOSE, m.data)
            self.send_frame(close)

    def _process_frame(self, m: Frame) -> Iterator[Event]:
        if m.opcode == Opcode.PING:
            self._process_ping(m)
            return
        if m.opcode == Opcode.CLOSE:
            self._process_close(m)
            return

        yield m

        if m.fin:
            if acc := self._accumulator:
                acc.append(m)
                msg = b''.join(m.data for m in acc)

                opcode = acc[0].opcode
                if opcode & Opcode.TEXT:
                    yield TextMessage(msg.decode())
                else:
                    yield BytesMessage(msg)

                acc.clear()

        else:
            self._accumulator.append(m)

    def pulse(self, *, timeout: float = 0) -> Iterator[Event]:
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

    def _get_cycle_value_from_timeout(self, timeout: float = 0) -> Optional[float]:
        t: Optional[float] = timeout
        if timeout == 0:
            t = self.default_timeout
        elif timeout == -1:
            t = None
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {t}')
        return t

    def receive(self, *, timeout: float = 0) -> Message:
        t = self._get_cycle_value_from_timeout(timeout)
        for event in self.cycle(t):
            if isinstance(event, Message):
                return event
        raise exceptions.TimeoutError

    def recv_bytes(self, *, timeout: float = 0) -> bytes:
        """Receive the next message. If it's a BytesMessage then return its payload,
        otherwise raise an UnexpectedMessageTypeException exception."""
        event = self.receive(timeout=timeout)
        if isinstance(event, BytesMessage):
            return event.data
        raise exceptions.UnexpectedMessageTypeException('string message received')

    def recv_text(self, *, timeout: float = 0) -> str:
        """Receive the next message. If it's a TextMessage then return its payload,
        otherwise raise an UnexpectedMessageTypeException exception."""
        event = self.receive(timeout=timeout)
        if isinstance(event, TextMessage):
            return event.data
        raise exceptions.UnexpectedMessageTypeException('bytes message received')

    def _send_close(self, code: Optional[int] = 1000, reason: str = '') -> None:
        data = b''
        if code is None:
            if reason:
                raise ValueError('cannot send a reason without a code')
        else:
            data = serialize_close(code, reason)

        close = Frame.make(Opcode.CLOSE, data)
        self.send_frame(close)
        self.set_state(ConnectionState.CLOSE_SENT)

    # Fix timeout = -2 for give me a default
    def close(self, code: Optional[int] = 1000, reason: str = '', *, timeout: float = 0) -> None:
        self._send_close()

        t = self._get_cycle_value_from_timeout(timeout)
        for event in self.cycle(t):
            if isinstance(event, Frame):
                if event.opcode == Opcode.CLOSE:
                    break

        self.shutdown()

    def shutdown(self) -> None:
        if self.close_code < 0:
            self.close_code = 1006

        self.set_state(ConnectionState.CLOSED)
