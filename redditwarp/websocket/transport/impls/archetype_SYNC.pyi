
from __future__ import annotations
from typing import Optional, Sequence, Mapping

from ...websocket_SYNC import WebSocket as BaseWebSocket

class WebSocket(BaseWebSocket):
    pass

def connect(
    url: str,
    *,
    subprotocols: Sequence[str] = (),
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = -2,
) -> WebSocket:
    pass
