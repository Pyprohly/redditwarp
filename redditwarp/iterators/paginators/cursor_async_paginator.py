
from __future__ import annotations
from typing import TypeVar, Optional

from .async_paginator import AsyncPaginator
from .interfaces import IResumable, IResettable

T = TypeVar('T')

class CursorAsyncPaginator(IResumable, IResettable, AsyncPaginator[T]):
    def __init__(self) -> None:
        super().__init__()
        self.cursor: Optional[str] = None
        self.available: Optional[bool] = None
        self.resuming = True

    def has_next(self) -> bool:
        if self.resuming:
            return True
        p = self.available
        if p is None:
            return False
        return p

    def resume(self) -> None:
        self.resuming = True

    def reset(self) -> None:
        self.cursor = None
        self.available = None
