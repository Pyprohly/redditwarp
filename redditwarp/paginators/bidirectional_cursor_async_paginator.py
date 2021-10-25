
from __future__ import annotations
from typing import TypeVar, Optional

from .cursor_async_paginator import CursorAsyncPaginator

T = TypeVar('T')

class BidirectionalCursorAsyncPaginator(CursorAsyncPaginator[T]):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        super().__init__(limit=limit)
        self.before: str = ''
        self.has_before: bool = True
        self.direction: bool = True

    def next_available(self) -> bool:
        return self.has_after if self.direction else self.has_before
