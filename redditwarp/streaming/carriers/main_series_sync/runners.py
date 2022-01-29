
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...util.sched import Scheduler

def run(client: Client, *streams: Iterator[float]) -> None:
    def _invoke_and_reschedule(itr: Iterator[float], shdlr: Scheduler) -> None:
        t = next(itr, -1)
        if t < 0:
            return
        shdlr.call_later(t, (lambda: _invoke_and_reschedule(itr, shdlr)))

    shdlr = Scheduler()
    for itr in streams:
        _invoke_and_reschedule(itr, shdlr)

    with client:
        shdlr.run()
