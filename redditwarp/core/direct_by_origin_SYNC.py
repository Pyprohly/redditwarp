
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from ..http.handler_SYNC import Handler
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

from urllib.parse import urlsplit

from ..http.delegating_handler_SYNC import DelegatingHandler

class DirectByOrigin(DelegatingHandler):
    def __init__(self,
        handler: Handler,
        directions: Mapping[str, Handler],
    ) -> None:
        super().__init__(handler)
        self.directions: Mapping[str, Handler] = directions
        ("")

    def _send(self, p: SendParams) -> Exchange:
        o = urlsplit(p.requisition.url)
        origin = f"{o.scheme}://{o.netloc}"
        direction = self.directions.get(origin)
        if direction is not None:
            return direction._send(p)
        return super()._send(p)
