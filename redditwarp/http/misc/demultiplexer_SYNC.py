
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping
if TYPE_CHECKING:
    from ..send_params import SendParams
    from ..exchange import Exchange
    from ..requisition import Requisition

from ..handler_SYNC import Handler
from ..delegating_handler_SYNC import DelegatingHandler


class DestinationUndeterminedException(Exception):
    pass

class DestinationCollisionException(Exception):
    pass


class Dispatcher(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.destinations: MutableMapping[Requisition, Handler] = {}

    def _send(self, p: SendParams) -> Exchange:
        try:
            dest = self.destinations[p.requisition]
        except KeyError:
            raise DestinationUndeterminedException from None
        return dest._send(p)

class Demultiplexer(DelegatingHandler):
    """The demultiplexer informs the dispatcher of the destination.

    Handler chain: demultiplexer -> handler -> dispatcher -> destination.
    """

    def __init__(self, handler: Handler, dispatcher: Dispatcher, destination: Handler) -> None:
        super().__init__(handler)
        self.dispatcher: Dispatcher = dispatcher
        self.destination: Handler = destination

    def _send(self, p: SendParams) -> Exchange:
        dests = self.dispatcher.destinations
        reqi = p.requisition
        dest = self.destination
        if dests.get(reqi, dest) is not dest:
            raise DestinationCollisionException
        dests[reqi] = dest
        try:
            xchg = super()._send(p)
        finally:
            del dests[reqi]
        return xchg

    def _close(self) -> None:
        super()._close()
        self.destination._close()
