
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...http.handler_SYNC import Handler
    from ...http.send_params import SendParams
    from ...http.exchange import Exchange

import time

from ...http.delegating_handler_SYNC import DelegatingHandler
from ...util.token_bucket import TokenBucket

class RateLimited(DelegatingHandler):
    def __init__(self, handler: Handler) -> None:
        super().__init__(handler)
        self._tb = TokenBucket(1, 1)

    def _send(self, p: SendParams) -> Exchange:
        time.sleep(self._tb.get_cooldown(1))
        self._tb.consume(1)
        return super()._send(p)
