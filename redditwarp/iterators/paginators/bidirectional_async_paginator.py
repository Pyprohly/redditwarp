
from __future__ import annotations
from typing import TypeVar, Optional

from .async_paginator import AsyncPaginator

T = TypeVar('T')

class BidirectionalAsyncPaginator(AsyncPaginator[T]):
    def __init__(self) -> None:
        super().__init__()
        self.has_prev = False
        self.back_cursor: Optional[str] = None
        self._forward = True

    def get_direction(self) -> bool:
        return self._forward

    def set_direction(self, value: bool) -> None:
        if self._forward != value:
            self._forward = value
            self.has_next, self.has_prev = self.has_prev, self.has_next

    def change_direction(self) -> None:
        self.set_direction(not self._forward)

    def reset(self) -> None:
        super().reset()
        self.has_prev = False
        self.back_cursor = None
