
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .send_params import SendParams
    from .exchange import Exchange

from .delegating_handler_SYNC import DelegatingHandler


class Invoker(DelegatingHandler):
    def send(self, p: SendParams) -> Exchange:
        return self._send(p)

    def close(self) -> None:
        self._close()
