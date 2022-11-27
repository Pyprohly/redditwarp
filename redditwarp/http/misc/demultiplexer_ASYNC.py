
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping
if TYPE_CHECKING:
    from ..send_params import SendParams
    from ..exchange import Exchange
    from ..requisition import Requisition

from ..handler_ASYNC import Handler
from ..delegating_handler_ASYNC import DelegatingHandler


class DestinationUndeterminedException(Exception):
    pass

class DestinationCollisionException(Exception):
    pass


class Dispatcher(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.destinations: MutableMapping[Requisition, Handler] = {}

    async def _send(self, p: SendParams) -> Exchange:
        try:
            dest = self.destinations[p.requisition]
        except KeyError:
            raise DestinationUndeterminedException from None
        return await dest._send(p)

class Demultiplexer(DelegatingHandler):
    def __init__(self, handler: Handler, dispatcher: Dispatcher, destination: Handler) -> None:
        super().__init__(handler)
        self.dispatcher: Dispatcher = dispatcher
        self.destination: Handler = destination

    async def _send(self, p: SendParams) -> Exchange:
        dests = self.dispatcher.destinations
        reqi = p.requisition
        dest = self.destination
        if dests.get(reqi, dest) is not dest:
            raise DestinationCollisionException
        dests[reqi] = dest
        try:
            xchg = await super()._send(p)
        finally:
            del dests[reqi]
        return xchg

    async def _close(self) -> None:
        await super()._close()
        await self.destination._close()
