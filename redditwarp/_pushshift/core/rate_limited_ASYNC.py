
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...http.handler_ASYNC import Handler
    from ...http.send_params import SendParams
    from ...http.exchange import Exchange

from ...util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

from ...http.delegating_handler_ASYNC import DelegatingHandler
from ...util.token_bucket import TokenBucket

class RateLimited(DelegatingHandler):
    def __init__(self, handler: Handler) -> None:
        super().__init__(handler)
        self._tb = TokenBucket(3, 1/2)

    async def _send(self, p: SendParams) -> Exchange:
        await asyncio.sleep(self._tb.get_cooldown(1))
        self._tb.consume(1)
        return await super()._send(p)
