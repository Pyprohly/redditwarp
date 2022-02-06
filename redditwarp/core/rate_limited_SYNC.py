
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

import time

from ..http.requestor_augmenter_SYNC import RequestorAugmenter
from ..util.token_bucket import TokenBucket

class RateLimited(RequestorAugmenter):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.reset: int = 0
        self.remaining: int = 0
        self.used: int = 0
        self._delta: float = 0.
        self._timestamp: float = time.monotonic()
        self._burst_control = TokenBucket(5, 1/2)

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        h = self._burst_control.hard_consume(1)
        if self.remaining < 1:
            time.sleep(self.reset)
        else:
            s = self.reset / self.remaining
            if not h or s >= 2:
                # The value 2 is chosen because, at worst, the user is allocated a 2
                # per second rate limit when a client credentials grant is used.

                time.sleep(s)

        response = self.requestor.send(request, timeout=timeout)

        now = time.monotonic()
        self._delta = now - self._timestamp
        self._timestamp = now

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
