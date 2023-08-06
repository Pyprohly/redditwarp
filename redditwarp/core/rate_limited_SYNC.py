
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..http.handler_SYNC import Handler
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

import time

from ..http.delegating_handler_SYNC import DelegatingHandler
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

    def _send(self, p: SendParams) -> Exchange:
        tb = self._tb
        s = 0.
        if self.remaining <= 1:
            s = self.reset
        elif self.reset > 0:
            tb.get_value()
            tb.rate = self.remaining / self.reset
            s = tb.get_cooldown(1)

        time.sleep(s)
        tb.consume(1)

        xchg = super()._send(p)

        now = time.monotonic()
        delta = now - self._timestamp
        self._timestamp = now

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
