
from __future__ import annotations
from typing import TypeVar, Optional

from .paginator import Paginator

T = TypeVar('T')

class BidirectionalPaginator(Paginator[T]):
    _forward: bool
    has_prev: bool

    def get_direction(self) -> bool:
        return self._forward

    def set_direction(self, value: Optional[bool] = None) -> None:
        if value is None:
            value = not self._forward
        if self._forward != value:
            self._forward = value
            self.has_next, self.has_prev = self.has_prev, self.has_next

    def __init__(self) -> None:
        super().__init__()
        self._forward = True
        self.back_cursor: Optional[str] = None
        self.has_prev = False
