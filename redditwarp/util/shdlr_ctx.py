pass
'''
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
if TYPE_CHECKING:
    from .shdlr import Scheduler

from contextvars import ContextVar
from contextlib import contextmanager

_shdlr_ctx_var: ContextVar[Scheduler] = ContextVar('shdlr_ctx')

def get_running_shdlr() -> Scheduler:
    try:
        return _shdlr_ctx_var.get()
    except LookupError:
        raise RuntimeError('no running scheduler') from None

@contextmanager
def enter_shdlr_ctx(shdlr: Scheduler) -> Iterator[None]:
    token = _shdlr_ctx_var.set(shdlr)
    try:
        yield
    finally:
        _shdlr_ctx_var.reset(token)
'''#'''
