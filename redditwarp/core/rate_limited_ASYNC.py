
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
        self._delta: float = 0.
        self._timestamp: float = time.monotonic()
        self._tb = TokenBucket(10, 1)
        self._lock = asyncio.Lock()
        self._datetime_extremum = datetime.min.replace(tzinfo=timezone.utc)

    async def _send(self, p: SendParams) -> Exchange:
        tb = self._tb
        async with self._lock:
            s = 0.
            if self.remaining <= 1:
                s = self.reset
            elif (w := self.reset / self.remaining) >= 2:
                # If the API wants us to wait for longer than two seconds then oblige.
                s = w

            if s:
                # Don't add tokens for the time spent sleeping here.
                bv = tb.get_value()
                await asyncio.sleep(s)
                tb.consume(tb.get_value() - bv)

            # The token bucket rate limiting is done in conjunction to the other rate limiting logic.
            await asyncio.sleep(tb.get_cooldown(1))
            tb.consume(1)

        xchg = await super()._send(p)

        now = time.monotonic()
        self._delta = now - self._timestamp
        self._timestamp = now

        date_string = xchg.response.headers['Date']
        dt = parsedate_to_datetime(date_string)
        if dt > self._datetime_extremum:
            self._datetime_extremum = dt

            headers = xchg.response.headers
            if 'x-ratelimit-reset' in headers:
                self.remaining = int(float(headers['x-ratelimit-remaining']))
                self.reset = int(headers['x-ratelimit-reset'])
                self.used = int(headers['x-ratelimit-used'])
            else:
                if self.reset > 0:
                    self.remaining -= 1
                    self.reset = max(0, self.reset - int(self._delta))
                    self.used += 1
                else:
                    self.remaining = 300
                    self.reset = 600
                    self.used = 0

        return xchg
