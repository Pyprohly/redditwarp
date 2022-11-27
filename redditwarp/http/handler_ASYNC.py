
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .send_params import SendParams
    from .exchange import Exchange


class Handler:
    async def _send(self, p: SendParams) -> Exchange:
        raise NotImplementedError

    async def _close(self) -> None:
        pass
