
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .send_params import SendParams
    from .exchange import Exchange

from .handler_SYNC import Handler


class DelegatingHandler(Handler):
    def __init__(self, handler: Handler) -> None:
        self._handler: Handler = handler

    def _send(self, p: SendParams) -> Exchange:
        return self._handler._send(p)

    def _close(self) -> None:
        self._handler._close()
