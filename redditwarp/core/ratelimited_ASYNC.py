
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from collections.abc import Mapping
    from ..http.requestor_ASYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from ..util.module_importing import lazy_import;
if 0: import asyncio
lazy_import%'asyncio'
import time

from ..http.requestor_ASYNC import RequestorDecorator
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

    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        s = 0.
        if self.remaining:
            # Can't use this for rate limiting because of concurrency.
            s = self.reset / self.remaining

        tb = self._rate_limiting_tb
        async with self._lock:
            # If the API wants us to sleep for longer than a second, do it.
            if s > 1:
                await self.sleep(s)

                # Don't add any tokens for the time spent sleeping here
                # as to have the effect of freezing the token bucket.
                tb.do_consume(s)

            if not tb.try_consume(1):
                await self.sleep(tb.cooldown(1))
                tb.do_consume(1)

        self._prev_request = self._last_request
        self._last_request = time.monotonic()

        response = await self.requestor.send(request, timeout=timeout, aux_info=aux_info)

        self.scan_ratelimit_headers(response.headers)
        return response

    def scan_ratelimit_headers(self, headers: Mapping[str, str]) -> None:
        if 'x-ratelimit-reset' in headers:
            self.reset = int(headers['x-ratelimit-reset'])
            self.remaining = int(float(headers['x-ratelimit-remaining']))
            self.used = int(headers['x-ratelimit-used'])
        elif self.reset > 0:
            self.reset -= int(self._last_request - self._prev_request)
            self.remaining -= 1
            self.used += 1
        else:
            self.reset = 100
            self.remaining = 200
            self.used = 0

    async def sleep(self, s: float) -> None:
        await asyncio.sleep(s)
