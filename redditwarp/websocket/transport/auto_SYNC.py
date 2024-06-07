
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Mapping
if TYPE_CHECKING:
    from ..websocket_SYNC import WebSocket

from .reg_SYNC import get_transport_adapter_module


def connect(
    url: str,
    *,
    subprotocols: Sequence[str] = (),
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = -2,
) -> WebSocket:
    return get_transport_adapter_module().connect(
        url=url,
        subprotocols=subprotocols,
        headers=headers,
        timeout=timeout,
    )
