
from ..delegating_handler_ASYNC import DelegatingHandler

class BlockClose(DelegatingHandler):
    async def _close(self) -> None:
        pass
