
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..http.handler_ASYNC import Handler
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

from ..util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from ..http.delegating_handler_ASYNC import DelegatingHandler
from ..util.token_bucket import TokenBucket

class RateLimited(DelegatingHandler):
    def __init__(self, handler: Handler) -> None:
        super().__init__(handler)
        self.remaining: int = 0
        ("")
        self.reset: int = 0
        ("")
        self.used: int = 0
        ("")
        self._timestamp: float = time.monotonic()
        self._tb = TokenBucket(capacity=10, rate=1)
        self._lock = asyncio.Lock()
        self._datetime = datetime.min.replace(tzinfo=timezone.utc)

    async def _send(self, p: SendParams) -> Exchange:
        async with self._lock:
            tb = self._tb
            s = 0.
            if self.remaining <= 1:
                s = self.reset
            elif self.reset > 0:
                tb.get_value()
                tb.rate = self.remaining / self.reset
                s = tb.get_cooldown(1)

            await asyncio.sleep(s)
            tb.consume(1)

        xchg = await super()._send(p)

        now = time.monotonic()
        delta = now - self._timestamp
        self._timestamp = now

        dt = parsedate_to_datetime(xchg.response.headers['Date'])
        if dt > self._datetime:
            self._datetime = dt

            headers = xchg.response.headers
            if 'x-ratelimit-reset' in headers:
                self.remaining = int(float(headers['x-ratelimit-remaining']))
                self.reset = int(headers['x-ratelimit-reset'])
                self.used = int(headers['x-ratelimit-used'])
            else:
                self.remaining -= 1
                self.reset -= int(delta)
                self.used += 1
                if self.reset <= 0:
                    self.remaining = 300
                    self.reset = 600
                    self.used = 0

        return xchg
