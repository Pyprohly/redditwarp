
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...util.sched import Scheduler


def run(*streams: Iterator[float], client: Optional[Client] = None) -> None:
    run_series(*streams, client=client)


def run_series(*streams: Iterator[float], client: Optional[Client] = None) -> None:
    def _invoke_and_reschedule(itr: Iterator[float], shdlr: Scheduler) -> None:
        try:
            t = next(itr)
        except StopIteration:
            pass
        else:
            shdlr.call_later(t, (lambda: _invoke_and_reschedule(itr, shdlr)))

    shdlr = Scheduler()
    for itr in streams:
        _invoke_and_reschedule(itr, shdlr)

    try:
        shdlr.run()

    finally:
        if client is not None:
            client.close()
