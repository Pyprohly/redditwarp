
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
if TYPE_CHECKING:
    from collections.abc import Mapping
    from ..http.requestor_SYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

import time

from ..http.requestor_decorator_SYNC import RequestorDecorator
from .token_bucket import TokenBucket

class RateLimited(RequestorDecorator):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.reset = 0
        self.remaining = 0
        self.used = 0
        self._burst_control_tb = TokenBucket(6, .5)
        self._prev_request = 0.
        self._last_request = time.monotonic()

    def send(self, request: Request, *, timeout: float = 0,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        s = 0.
        if self.remaining:
            s = self.reset / self.remaining

        h = self._burst_control_tb.hard_consume(1)
        if h and s < 1:
            # If a token was consumed then burst this request, but only
            # if the API didn't want us to wait for more than a second.
            s = 0

        self.sleep(s)

        self._prev_request = self._last_request
        self._last_request = time.monotonic()

        response = self.requestor.send(request, timeout=timeout, aux_info=aux_info)

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

    def sleep(self, s: float) -> None:
        time.sleep(s)
