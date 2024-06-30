
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

from ..http.delegating_handler_SYNC import DelegatingHandler


class FollowRedirectsValueNoneMeansTrue(DelegatingHandler):
    def _send(self, p: SendParams) -> Exchange:
        if p.follow_redirects is None:
            p.follow_redirects = True
        return self._handler._send(p)

class FollowRedirectsValueNoneMeansFalse(DelegatingHandler):
    def _send(self, p: SendParams) -> Exchange:
        if p.follow_redirects is None:
            p.follow_redirects = False
        return self._handler._send(p)
