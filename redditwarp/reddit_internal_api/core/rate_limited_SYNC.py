
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...http.requestor_SYNC import Requestor
    from ...http.request import Request
    from ...http.response import Response

import time

from ...http.requestor_augmenter_SYNC import RequestorAugmenter
from ...util.token_bucket import TokenBucket

class RateLimited(RequestorAugmenter):
    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self._tb = TokenBucket(3, 1/2)

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        time.sleep(self._tb.get_cooldown(1))
        self._tb.do_consume(1)
        return self.requestor.send(request, timeout=timeout)
