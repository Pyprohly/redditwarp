
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from collections.abc import MutableSequence, Iterator
    from ..events import Event, Frame

# https://pypi.org/project/websocket-client/
import websocket  # type: ignore[import]

from ..websocket_connection_abstract_base_SYNC import WebSocketConnectionAbstractBase
from .. import exceptions
from .. import events
from ..const import Opcode, Side

class WebSocketClient(WebSocketConnectionAbstractBase):
    side = Side.CLIENT

    def __init__(self, ws: websocket.WebSocket):
        super().__init__()
        self.ws = ws
        self._processing_data_frames = False
        self._data_frames_are_text = True
        self._continuation_data_buffer: MutableSequence[bytes] = []

    def send_frame(self, m: Frame) -> None:
        super().send_frame(m)
        frm = websocket.ABNF.create_frame(opcode=m.opcode, data=m.data, fin=int(m.fin))
        try:
            self.ws.send_frame(frm)
        except Exception as e:
            raise exceptions.TransportError from e

    def _load_next_frame(self, *, timeout: float = 0) -> Frame:
        t: Optional[float] = timeout
        if timeout == -1:
            t = None
        elif timeout == 0:
            t = self.default_timeout
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {t}')

        self.ws.timeout = t

        try:
            _, frm = self.ws.recv_data_frame(True)
        except websocket.WebSocketTimeoutException as e:
            raise exceptions.TimeoutError from e
        except Exception as e:
            raise exceptions.TransportError from e

        fin = bool(frm.fin)
        opcode = frm.opcode
        data = frm.data if isinstance(frm.data, bytes) else frm.data.encode()
        return events.Frame(
            opcode=Opcode(frm.opcode),
            fin=fin,
            data=data,
        )

    def close(self, code: Optional[int] = 1000, reason: str = '', *, timeout: float = 0) -> None:
        t: Optional[float] = timeout
        if timeout == -1:
            t = None
        elif timeout == 0:
            t = self.default_timeout
        elif timeout < 0:
            raise ValueError(f'invalid timeout value: {t}')

        try:
            self.ws.close(code, reason.encode(), timeout=t)
        except Exception as e:
            raise exceptions.TransportError from e


def connect(url: str, *, subprotocols: Sequence[str] = ()) -> WebSocketClient:
    ws = websocket.create_connection(url, fire_cont_frame=True)
    return WebSocketClient(ws)
