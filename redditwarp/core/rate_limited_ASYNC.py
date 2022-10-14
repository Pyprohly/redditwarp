
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ..http.requestor_ASYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from ..util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from ..http.requestor_augmenter_ASYNC import RequestorAugmenter
from ..util.token_bucket import TokenBucket

class RateLimited(RequestorAugmenter):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.reset: int = 0
        self.remaining: int = 0
        self.used: int = 0
        self._delta: float = 0.
        self._timestamp: float = time.monotonic()
        self._tb = TokenBucket(10, 1)
        self._lock = asyncio.Lock()
        self._datetime_extremum = datetime.min.replace(tzinfo=timezone.utc)

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        tb = self._tb
        async with self._lock:
            s = 0.
            if self.remaining < 2:
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

        response = await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)

        now = time.monotonic()
        self._delta = now - self._timestamp
        self._timestamp = now

        date_string = response.headers['Date']
        dt = parsedate_to_datetime(date_string)
        if dt > self._datetime_extremum:
            self._datetime_extremum = dt

            headers = response.headers
            if 'x-ratelimit-reset' in headers:
                self.reset = int(headers['x-ratelimit-reset'])
                self.remaining = int(float(headers['x-ratelimit-remaining']))
                self.used = int(headers['x-ratelimit-used'])
            else:
                if self.reset > 0:
                    self.reset = max(self.reset - int(self._delta), 0)
                    self.remaining -= 1
                    self.used += 1
                else:
                    self.reset = 600
                    self.remaining = 300
                    self.used = 0

        return response
