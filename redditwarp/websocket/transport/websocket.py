
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from collections.abc import Iterator

# https://pypi.org/project/websocket-client/
import websocket  # type: ignore[import]

from .SYNC import register
from ..websocket_connection_SYNC import HalfImplementedWebSocketConnection
from .. import exceptions
from ..events import Event, Frame
from ..const import Opcode, Side, ConnectionState
from ..util import parse_close

class WebSocketClient(HalfImplementedWebSocketConnection):
    side = Side.CLIENT

    def __init__(self, ws: websocket.WebSocket):
        super().__init__()
        self.ws = ws

    def _get_necessary_timeout(self, timeout: float = -2) -> Optional[float]:
        t: Optional[float] = timeout
        if timeout == -2:
            t = self.default_timeout
        elif timeout == -1:
            t = None
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {timeout}')
        return t

    def send_frame(self, m: Frame) -> None:
        super().send_frame(m)
        frm = websocket.ABNF.create_frame(opcode=m.opcode, data=m.data, fin=int(m.fin))
        try:
            self.ws.send_frame(frm)
        except Exception as e:
            raise exceptions.TransportError from e

    def _load_next_frame(self, *, timeout: float = -2) -> Frame:
        t = self._get_necessary_timeout(timeout)
        self.ws.timeout = t
        try:
            _, frm = self.ws.recv_data_frame(True)
        except websocket.WebSocketTimeoutException as e:
            raise exceptions.TimeoutError from e
        except websocket.WebSocketConnectionClosedException as e:
            raise exceptions.ConnectionClosedException from e
        except Exception as e:
            raise exceptions.TransportError from e

        return Frame(
            opcode=Opcode(frm.opcode),
            fin=bool(frm.fin),
            data=(frm.data if isinstance(frm.data, bytes) else frm.data.encode()),
        )

    def _process_ping(self, m: Frame) -> Iterator[Event]:
        yield m

    def _process_close(self, m: Frame) -> Iterator[Event]:
        self.set_state(ConnectionState.CLOSE_RECEIVED)
        self.close_code, self.close_reason = parse_close(m.data)
        yield m

    def _process_frame(self, m: Frame) -> Iterator[Event]:
        yield from super()._process_frame(m)

    def _send_close(self, code: Optional[int] = 1000, reason: str = '') -> None:
        try:
            self.ws.send_close(code, reason.encode())
        except Exception as e:
            raise exceptions.TransportError from e

    def close(self, code: Optional[int] = 1000, reason: str = '', *, waitfor: float = -2) -> None:
        super().close(code, reason, waitfor=waitfor)

    def shutdown(self) -> None:
        super().shutdown()
        try:
            self.ws.shutdown()
        except Exception as e:
            raise exceptions.TransportError from e


def connect(url: str, *, subprotocols: Sequence[str] = (), timeout: float = -2) -> WebSocketClient:
    t: Optional[float] = timeout
    if timeout == -2:
        t = HalfImplementedWebSocketConnection.DEFAULT_TIMEOUT
    elif timeout == -1:
        t = None
    elif timeout < 0:
        raise ValueError(f'invalid timeout value: {timeout}')

    try:
        ws = websocket.create_connection(url, fire_cont_frame=True, timeout=t)
    except websocket.WebSocketTimeoutException:
        raise exceptions.TimeoutError
    return WebSocketClient(ws)


name = websocket.__name__
version = websocket.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    connect=connect,
)
