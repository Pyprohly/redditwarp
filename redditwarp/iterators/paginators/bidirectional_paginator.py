
from __future__ import annotations
from typing import TypeVar, Optional

from .paginator import Paginator

T = TypeVar('T')

class BidirectionalPaginator(Paginator[T]):
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

    def _set_cursors(self, c1: Optional[str], c2: Optional[str]) -> None:
        self.cursor = c1
        self.back_cursor = c2

        if not self._forward:
            c1, c2 = c2, c1
        self.has_next = bool(c1)
        self.has_prev = bool(c2)
