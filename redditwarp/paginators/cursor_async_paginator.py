
from __future__ import annotations
from typing import TypeVar, Optional

from .async_paginator import AsyncPaginator

T = TypeVar('T')

class CursorAsyncPaginator(AsyncPaginator[T]):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        super().__init__(limit=limit)
        self.after: str = ''
        self.has_after: bool = True

    def next_available(self) -> bool:
        return self.has_after
