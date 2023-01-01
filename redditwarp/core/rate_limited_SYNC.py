
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
        self.reset: int = 0
        self.remaining: int = 0
        self.used: int = 0
        self._delta: float = 0.
        self._timestamp: float = time.monotonic()
        self._burst_control = TokenBucket(5, 1/2)

    def _send(self, p: SendParams) -> Exchange:
        h = self._burst_control.hard_consume(1)
        s = 0.
        if self.remaining <= 1:
            s = self.reset
        else:
            w = self.reset / self.remaining
            if not h or w >= 2:
                # Burst this request, but only if the API didn't
                # want us to wait for more than two seconds.
                # Use 2 because at worst the user is allocated a 2/s (600/300)
                # rate limit when a client credentials grant is used.
                s = w

        time.sleep(s)

        xchg = super()._send(p)

        now = time.monotonic()
        self._delta = now - self._timestamp
        self._timestamp = now

        headers = xchg.response.headers
        if 'x-ratelimit-reset' in headers:
            self.reset = int(headers['x-ratelimit-reset'])
            self.remaining = int(float(headers['x-ratelimit-remaining']))
            self.used = int(headers['x-ratelimit-used'])
        else:
            if self.reset > 0:
                self.reset = max(0, self.reset - int(self._delta))
                self.remaining -= 1
                self.used += 1
            else:
                self.reset = 600
                self.remaining = 300
                self.used = 0

        return xchg
