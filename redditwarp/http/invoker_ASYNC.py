
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .send_params import SendParams
    from .exchange import Exchange

from .delegating_handler_ASYNC import DelegatingHandler


class Invoker(DelegatingHandler):
    async def send(self, p: SendParams) -> Exchange:
        return await self._send(p)

    async def close(self) -> None:
        await self._close()
