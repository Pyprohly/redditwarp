
from typing import Union, Iterator, Optional, MutableSequence

import time

from .const import Opcode, ConnectionState, Side
from . import exceptions
from . import events
from .events import Frame, Message, BytesMessage, TextMessage
from .utils import parse_close, serialize_close

class WebSocketConnection:
    DEFAULT_WAITTIME: float = 10.
    SIDE: int = Side.NONE

    @property
    def default_timeout(self) -> float:
        return self.default_waittime

    @default_timeout.setter
    def default_timeout(self, value: float) -> None:
        self.default_waittime: float = value

    def __init__(self) -> None:
        self.default_waittime = self.DEFAULT_WAITTIME
        self.state: ConnectionState = ConnectionState.OPEN
        self.close_code: int = -1
        self.close_reason: str = ''
        self.subprotocol: str = ''

    def __iter__(self) -> Iterator[object]:
        yield from self.cycle(-1)

    def _send_frame_impl(self, m: Frame) -> None:
        pass

    def send_frame(self, m: Frame) -> None:
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        elif self.state == ConnectionState.CLOSING:
            if m.opcode != Opcode.CLOSE:
                raise exceptions.InvalidStateException('cannot send non-close frame in closing state')
        elif self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'cannot send frame in {self.state.name!r} state')

        self._send_frame_impl(m)

    def send_text(self, data: str) -> None:
        self.send_frame(Frame.make(Opcode.TEXT, data.encode()))

    def send_bytes(self, data: bytes) -> None:
        self.send_frame(Frame.make(Opcode.BINARY, data))

    def send(self, data: Union[str, bytes]) -> None:
        if isinstance(data, str):
            self.send_text(data)
        else:
            self.send_bytes(data)

    def _pulse_impl(self, *, timeout: float = -2) -> Iterator[object]:
        return
        yield

    def pulse(self, *, timeout: float = -2) -> Iterator[object]:
        """Process one frame’s worth of incoming data and possibly generate events for it."""
        if self.state == ConnectionState.CLOSED:
            raise exceptions.ConnectionClosedException
        if self.state not in {ConnectionState.OPEN, ConnectionState.CLOSING}:
            raise exceptions.InvalidStateException(f'cannot ingest frame in {self.state.name!r} state')

        yield from self._pulse_impl(timeout=timeout)

    def cycle(self, t: float = -1) -> Iterator[object]:
        """Yield events from `self.pulse()` over `t` seconds."""
        if t == -1:
            while True:
                for event in self.pulse(timeout=-1):
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
                    for event in self.pulse(timeout=tv):
                        yield event
                        if isinstance(event, events.ConnectionClosed):
                            return
                except exceptions.TimeoutException:
                    return

                now = time.monotonic()
                tv -= now - tn
                tn = now

    def receive(self, *, timeout: float = -2) -> Message:
        for event in self.cycle(timeout):
            if isinstance(event, Message):
                return event
            elif isinstance(event, events.ConnectionClosed):
                raise exceptions.ConnectionClosedException
        raise exceptions.TimeoutException

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

    def _send_close_frame_impl(self, code: Optional[int] = 1000, reason: str = '') -> None:
        data = b''
        if code is not None:
            data = serialize_close(code, reason)
        close = Frame.make(Opcode.CLOSE, data)
        self.send_frame(close)

    def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        if code is None and reason:
            raise ValueError('cannot send a reason without a code')

        if self.state == ConnectionState.CLOSED:
            return
        if self.state != ConnectionState.OPEN:
            raise exceptions.InvalidStateException(f'operation not permitted in {self.state.name!r} state')

        self.state = ConnectionState.CLOSING

        self._send_close_frame_impl(code, reason)

        for _ in self.cycle(waitfor):
            pass

        self.shutdown()

    def shutdown(self) -> None:
        if self.close_code < 0:
            self.close_code = 1006
        self.state = ConnectionState.CLOSED



class PulsePartiallyImplementedWebSocketConnection(WebSocketConnection):
    def __init__(self) -> None:
        super().__init__()
        self._accumulator: MutableSequence[Frame] = []

    def _process_ping_frame(self, m: Frame) -> Iterator[object]:
        if self.state not in {ConnectionState.CLOSING, ConnectionState.CLOSED}:
            pong = Frame.make(Opcode.PONG, m.data)
            self.send_frame(pong)
        yield m

    def _process_close_frame(self, m: Frame) -> Iterator[object]:
        self.state: ConnectionState = ConnectionState.CLOSING
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

    def _process_data_frame(self, m: Frame) -> Iterator[object]:
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

    def _process_frame(self, m: Frame) -> Iterator[object]:
        if m.opcode == Opcode.PING:
            yield from self._process_ping_frame(m)
        elif m.opcode == Opcode.CLOSE:
            yield from self._process_close_frame(m)
        elif m.opcode in {Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY}:
            yield from self._process_data_frame(m)

    def _load_next_frame(self, *, timeout: float = -2) -> Frame:
        raise NotImplementedError

    def _pulse_impl(self, *, timeout: float = -2) -> Iterator[object]:
        frame = self._load_next_frame(timeout=timeout)
        yield from self._process_frame(frame)
