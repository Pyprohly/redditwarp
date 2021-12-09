
from typing import Union, Iterator, Optional, MutableSequence

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

    def __iter__(self) -> Iterator[Event]:
        yield from self.cycle()

    def recv_bytes(self, *, timeout: float = -2) -> bytes:
        """Receive the next message. If it's a BytesMessage then return its payload,
        otherwise raise an MessageTypeMismatchException exception."""
        event = self.receive(timeout=timeout)
        if isinstance(event, BytesMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('string message received')

    def recv(self, *, timeout: float = -2) -> bytes:
        return self.recv_bytes(timeout=timeout)

    def recv_text(self, *, timeout: float = -2) -> str:
        """Receive the next message. If it's a TextMessage then return its payload,
        otherwise raise an MessageTypeMismatchException exception."""
        event = self.receive(timeout=timeout)
        if isinstance(event, TextMessage):
            return event.data
        raise exceptions.MessageTypeMismatchException('bytes message received')

    def cycle(self, t: float = -1) -> Iterator[Event]:
        """Yield events from `self.pulse()` over `t` seconds."""
        if t == -1:
            while True:
                for event in self.pulse(timeout=-1):
                    yield event
                    if isinstance(event, events.ConnectionClosed):
                        return

        else:
            tv = t
            tn = time.monotonic()
            while tv > 0:
                try:
                    for event in self.pulse(timeout=tv):
                        yield event
                        if isinstance(event, events.ConnectionClosed):
                            return
                except exceptions.TimeoutException:
                    return

                now = time.monotonic()
                tv -= now - tn
                tn = now

    def shutdown(self) -> None:
        if self.close_code < 0:
            self.close_code = 1006

        self.state = ConnectionState.CLOSED

    def send_frame(self, m: Frame) -> None:
        raise NotImplementedError

    def send_text(self, data: str) -> None:
        raise NotImplementedError

    def send_bytes(self, data: bytes) -> None:
        raise NotImplementedError

    def send(self, data: Union[str, bytes]) -> None:
        raise NotImplementedError

    def pulse(self, *, timeout: float = -2) -> Iterator[Event]:
        """Process one frame’s worth of incoming data and possibly generate events for it."""
        raise NotImplementedError
        yield

    def receive(self, *, timeout: float = -2) -> Message:
        raise NotImplementedError

    def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        raise NotImplementedError


class PartiallyImplementedWebSocketConnection(WebSocketConnection):
    def __init__(self) -> None:
        super().__init__()
        self._accumulator: MutableSequence[Frame] = []

    def send_frame(self, m: Frame) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
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

    def _process_ping_frame(self, m: Frame) -> Iterator[Event]:
        if self.state not in {ConnectionState.CLOSE_RECEIVED, ConnectionState.CLOSED}:
            pong = Frame.make(Opcode.PONG, m.data)
            self.send_frame(pong)
        yield m

    def _process_close_frame(self, m: Frame) -> Iterator[Event]:
        self.state = ConnectionState.CLOSE_RECEIVED
        self.close_code: int
        self.close_reason: str
        self.close_code, self.close_reason = parse_close(m.data)

        if self.state == ConnectionState.OPEN:
            close = Frame.make(Opcode.CLOSE, m.data)
            try:
                self.send_frame(close)
            except exceptions.ConnectionClosedException:
                pass

        self.shutdown()

        yield m
        yield events.ConnectionClosed()

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

    def _process_frame(self, m: Frame) -> Iterator[Event]:
        if m.opcode == Opcode.PING:
            yield from self._process_ping_frame(m)
        elif m.opcode == Opcode.CLOSE:
            yield from self._process_close_frame(m)
        elif m.opcode in {Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY}:
            yield from self._process_data_frame(m)

    def _load_next_frame(self, *, timeout: float = -2) -> Frame:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name} state')
        raise NotImplementedError

    def pulse(self, *, timeout: float = -2) -> Iterator[Event]:
        """Process one frame’s worth of incoming data and possibly generate events for it."""
        frame = self._load_next_frame(timeout=timeout)
        yield from self._process_frame(frame)

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

    def receive(self, *, timeout: float = -2) -> Message:
        t = self._get_cycle_value_from_timeout(timeout)
        for event in self.cycle(t):
            if isinstance(event, Message):
                return event
            elif isinstance(event, events.ConnectionClosed):
                raise exceptions.ConnectionClosedException()
        raise exceptions.TimeoutException

    def _send_close_frame(self, code: Optional[int] = 1000, reason: str = '') -> None:
        data = b''
        if code is not None:
            data = serialize_close(code, reason)

        close = Frame.make(Opcode.CLOSE, data)
        self.send_frame(close)

    def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None and reason:
            raise ValueError('cannot send a reason without a code')

        t = self._get_cycle_value_from_waitfor(waitfor)

        if self.state != ConnectionState.OPEN:
            return

        self._send_close_frame(code, reason)

        self.state: ConnectionState = ConnectionState.CLOSE_SENT

        for event in self.cycle(t):
            if isinstance(event, Frame):
                if event.opcode == Opcode.CLOSE:
                    break

        self.shutdown()
