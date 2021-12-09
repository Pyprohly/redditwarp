
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Mapping
    from ..http.requestor_ASYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from ..util.imports import lazy_import
if TYPE_CHECKING:
    import asyncio
else:
    lazy_import % 'asyncio'

import time

from ..http.requestor_augmenter_ASYNC import RequestorAugmenter
from ..util.token_bucket import TokenBucket

class RateLimited(RequestorAugmenter):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.reset: int = 0
        self.remaining: int = 0
        self.used: int = 0
        self._rate_limiter = TokenBucket(10, 1)
        self._prev_request_time = 0.
        self._last_request_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        s: float = self.reset
        if self.remaining > 0:
            # Can't rely solely on this because of concurrency.
            s = self.reset / self.remaining

        tb = self._rate_limiter
        async with self._lock:
            # If the API wants us to wait for longer than two seconds, oblige.
            if s >= 2:
                await self.sleep(s)
                # Don't add tokens for the time spent sleeping here.
                tb.do_consume(s)

            if not tb.try_consume(1):
                await self.sleep(tb.get_cooldown(1))
                tb.do_consume(1)

        response = await self.requestor.send(request, timeout=timeout)

        self._prev_request_time = self._last_request_time
        self._last_request_time = time.monotonic()

        self.scan_ratelimit_headers(response.headers)
        return response

    def scan_ratelimit_headers(self, headers: Mapping[str, str]) -> None:
        if 'x-ratelimit-reset' in headers:
            self.reset = int(headers['x-ratelimit-reset'])
            self.remaining = int(float(headers['x-ratelimit-remaining']))
            self.used = int(headers['x-ratelimit-used'])
        elif self.reset > 0:
            self.reset = max(0, self.reset - int(self._last_request_time - self._prev_request_time))
            self.remaining -= 1
            self.used += 1
        else:
            self.reset = 600
            self.remaining = 300
            self.used = 0

    async def sleep(self, s: float) -> None:
        await asyncio.sleep(s)
