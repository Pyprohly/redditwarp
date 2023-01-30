
from __future__ import annotations
from typing import Iterator

from ..util.shdlr import Scheduler


def flow(*streams: Iterator[float]) -> None:
    flow_series(*streams)

def flow_series(*streams: Iterator[float]) -> None:
    def _invoke_and_reschedule(itr: Iterator[float], shdlr: Scheduler) -> None:
        try:
            t = next(itr)
        except StopIteration:
            return
        shdlr.call_later(t, (lambda: _invoke_and_reschedule(itr, shdlr)))

    shdlr = Scheduler()
    for itr in streams:
        _invoke_and_reschedule(itr, shdlr)
    shdlr.run()
