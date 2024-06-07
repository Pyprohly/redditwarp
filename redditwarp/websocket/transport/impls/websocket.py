
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Mapping
if TYPE_CHECKING:
    from collections.abc import Iterator

# https://pypi.org/project/websocket-client/
import websocket  # type: ignore[import]

from ...websocket_SYNC import PulsePartiallyImplementedWebSocketConnection, DEFAULT_WAITTIME
from ... import exceptions
from ... import events
from ...events import Frame
from ...const import Opcode, ConnectionState
from ...utils import parse_close


def _get_necessary_timeout(timeout: float = -2) -> Optional[float]:
    t: Optional[float] = timeout
    if timeout == -2:
        t = DEFAULT_WAITTIME
    elif timeout == -1:
        t = None
    elif timeout < 0:
        raise ValueError(f'invalid timeout value: {timeout}')
    return t


class WebSocket(PulsePartiallyImplementedWebSocketConnection):
    def __init__(self, ws: websocket.WebSocket) -> None:
        super().__init__()
        self.ws: websocket.WebSocket = ws
        ("")

    def _send_frame_impl(self, m: Frame) -> None:
        frm = websocket.ABNF.create_frame(opcode=m.opcode, data=m.data.decode(), fin=int(m.fin))
        try:
            self.ws.send_frame(frm)
        except websocket.WebSocketConnectionClosedException as cause:
            if self.state != ConnectionState.CLOSED:
                raise Exception('assertion')
            raise exceptions.ConnectionClosedException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

    def _load_next_frame(self, *, timeout: float = -2) -> Optional[Frame]:
        self.ws.timeout = _get_necessary_timeout(timeout)
        try:
            _, frm = self.ws.recv_data_frame(True)
        except websocket.WebSocketTimeoutException as cause:
            raise exceptions.TimeoutException from cause
        except websocket.WebSocketConnectionClosedException as cause:
            if self.state != ConnectionState.CLOSED:
                raise Exception('assertion')
            raise exceptions.ConnectionClosedException from cause
        except websocket.WebSocketProtocolException as cause:
            if "Invalid close opcode" in str(cause):
                self.close_code = cause.args[1]
                return None
            raise
        except Exception as cause:
            raise exceptions.TransportError from cause

        return Frame(
            opcode=Opcode(frm.opcode),
            fin=bool(frm.fin),
            data=(frm.data if isinstance(frm.data, bytes) else frm.data.encode()),
        )

    def _process_ping_frame(self, m: Frame) -> Iterator[object]:
        yield m

    def _process_close_frame(self, m: Frame) -> Iterator[object]:
        yield m
        self.close_code: int
        self.close_reason: str
        self.close_code, self.close_reason = parse_close(m.data)
        self.state = ConnectionState.CLOSED
        yield events.ConnectionClosed()

    def _send_close_frame_impl(self, code: Optional[int] = 1000, reason: str = '') -> None:
        if code is None:
            raise RuntimeError('must specify a close code with websocket-client library')

        try:
            self.ws.send_close(code, reason.encode())
        except Exception as cause:
            raise exceptions.TransportError from cause

    def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        super().close(code, reason, waitfor=waitfor)
        try:
            self.ws.shutdown()  # type: ignore[no-untyped-call]
        except Exception as cause:
            raise exceptions.TransportError from cause


def connect(
    url: str,
    *,
    subprotocols: Sequence[str] = (),
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = -2,
) -> WebSocket:
    t = _get_necessary_timeout(timeout)
    try:
        ws = websocket.create_connection(
            url,
            fire_cont_frame=True,
            timeout=t,
            suppress_origin=True,
            header=headers,
            subprotocols=subprotocols,
        )
    except websocket.WebSocketTimeoutException as cause:
        raise exceptions.TimeoutException from cause
    except Exception as cause:
        raise exceptions.TransportError from cause
    wsc = WebSocket(ws)
    wsc.subprotocol = ws.subprotocol or ''
    return wsc


name: str = 'websocket-client'
version: str = websocket.__version__
