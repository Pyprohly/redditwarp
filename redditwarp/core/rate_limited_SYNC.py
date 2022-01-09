
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Mapping
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
        self._delta = 0.
        self._timestamp = time.monotonic()
        self._burst_control = TokenBucket(5, .5)

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        s: float = self.reset
        if self.remaining > 0:
            s = self.reset / self.remaining

        h = self._burst_control.hard_consume(1)
        if h and s < 2 and self.remaining > 20:
            # Burst this request, but only if the API didn't
            # want us to wait for more than two seconds, and
            # we have more than 20 requests remaining.
            s = 0

        time.sleep(s)

        response = self.requestor.send(request, timeout=timeout)

        now = time.monotonic()
        self._delta = now - self._timestamp
        self._timestamp = now

        self.scan_ratelimit_headers(response.headers)
        return response

    def scan_ratelimit_headers(self, headers: Mapping[str, str]) -> None:
        if 'x-ratelimit-reset' in headers:
            self.reset = int(headers['x-ratelimit-reset'])
            self.remaining = int(float(headers['x-ratelimit-remaining']))
            self.used = int(headers['x-ratelimit-used'])
        elif self.reset > 0:
            self.reset = max(0, self.reset - int(self._delta))
            self.remaining -= 1
            self.used += 1
        else:
            self.reset = 600
            self.remaining = 300
            self.used = 0
