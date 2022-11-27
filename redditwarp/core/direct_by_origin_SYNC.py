
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Optional
if TYPE_CHECKING:
    from ..http.handler_SYNC import Handler
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

from urllib.parse import urlsplit

from ..http.delegating_handler_SYNC import DelegatingHandler

class DirectByOrigin(DelegatingHandler):
    def __init__(self,
        handler: Handler,
        directions: Optional[Mapping[str, Handler]] = None,
    ) -> None:
        super().__init__(handler)
        self.directions: Mapping[str, Handler] = {} if directions is None else directions

    def _send(self, p: SendParams) -> Exchange:
        origin = f"{(o := urlsplit(p.requisition.url)).scheme}://{o.netloc}"
        direction = self.directions.get(origin)
        if direction is not None:
            return direction._send(p)
        return super()._send(p)
