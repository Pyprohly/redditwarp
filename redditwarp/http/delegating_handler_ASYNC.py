
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .send_params import SendParams
    from .exchange import Exchange

from .handler_ASYNC import Handler


class DelegatingHandler(Handler):
    def __init__(self, handler: Handler) -> None:
        self._handler: Handler = handler

    async def _send(self, p: SendParams) -> Exchange:
        return await self._handler._send(p)

    async def _close(self) -> None:
        await self._handler._close()
