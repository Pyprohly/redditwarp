
from __future__ import annotations
from typing import TypeVar, Optional

from .cursor_paginator import CursorPaginator

T = TypeVar('T')

class BidirectionalCursorPaginator(CursorPaginator[T]):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        super().__init__(limit=limit)
        self.before = ''
        self.has_before = True
        self.direction = True

    def next_available(self) -> bool:
        return self.has_after if self.direction else self.has_before
