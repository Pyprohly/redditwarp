
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Mapping
if TYPE_CHECKING:
    from ..websocket_ASYNC import WebSocket

from .reg_ASYNC import get_transport_adapter_module


async def connect(
    url: str,
    *,
    subprotocols: Sequence[str] = (),
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = -2,
) -> WebSocket:
    return await get_transport_adapter_module().connect(
        url=url,
        subprotocols=subprotocols,
        headers=headers,
        timeout=timeout,
    )
