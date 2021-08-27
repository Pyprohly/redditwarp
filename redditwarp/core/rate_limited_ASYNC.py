
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
    lazy_import('asyncio')

import time

from ..http.requestor_decorator_ASYNC import RequestorDecorator
from .token_bucket import TokenBucket

class RateLimited(RequestorDecorator):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.reset = 0
        self.remaining = 0
        self.used = 0
        self._rate_limiting_tb = TokenBucket(10, 1)
        self._prev_request = 0.
        self._last_request = time.monotonic()
        self._lock = asyncio.Lock()

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        s: float = self.reset
        if self.remaining > 0:
            # Note: value not precise due to concurrency.
            s = self.reset / self.remaining

        tb = self._rate_limiting_tb
        async with self._lock:
            # If the API wants us to wait for longer than a second, oblige.
            if s >= 1:
                await self.sleep(s)
                # And don't add tokens for the time spent sleeping here.
                tb.do_consume(s)

            # If not enough tokens...
            if not tb.try_consume(1):
                # Wait until enough...
                await self.sleep(tb.get_cooldown(1))
                # Immediately consume...
                tb.do_consume(1)
                # Then proceed.

        self._prev_request = self._last_request
        self._last_request = time.monotonic()

        response = await self.requestor.send(request, timeout=timeout)

        self.scan_ratelimit_headers(response.headers)
        return response

    def scan_ratelimit_headers(self, headers: Mapping[str, str]) -> None:
        if 'x-ratelimit-reset' in headers:
            self.reset = int(headers['x-ratelimit-reset'])
            self.remaining = int(float(headers['x-ratelimit-remaining']))
            self.used = int(headers['x-ratelimit-used'])
        elif self.reset > 0:
            self.reset = max(0, self.reset - int(self._last_request - self._prev_request))
            self.remaining -= 1
            self.used += 1
        else:
            self.reset = 100
            self.remaining = 200
            self.used = 0

    async def sleep(self, s: float) -> None:
        await asyncio.sleep(s)
