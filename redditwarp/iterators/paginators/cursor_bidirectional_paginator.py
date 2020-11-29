
from __future__ import annotations
from typing import TypeVar, Optional

from .bidirectional_paginator import BidirectionalPaginator
from .interfaces import IResumable, IResettable

T = TypeVar('T')

class CursorBidirectionalPaginator(IResumable, IResettable, BidirectionalPaginator[T]):
    def __init__(self) -> None:
        super().__init__()
        self.forward_cursor: Optional[str] = None
        self.backward_cursor: Optional[str] = None
        self.forward_available: Optional[bool] = None
        self.backward_available: Optional[bool] = None
        self.resuming = True

    def has_next(self) -> bool:
        if self.resuming:
            return True
        p = self.forward_available if self.get_direction() else self.backward_available
        return p or False

    def resume(self) -> None:
        self.resuming = True

    def reset(self) -> None:
        self.forward_cursor = None
        self.backward_cursor = None
        self.forward_available = None
        self.backward_available = None
