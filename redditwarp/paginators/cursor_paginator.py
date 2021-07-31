
from __future__ import annotations
from typing import TypeVar, Optional

from .paginator import Paginator

T = TypeVar('T')

class CursorPaginator(Paginator[T]):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        super().__init__(limit=limit)
        self.after = ''
        self.has_after = True

    def next_available(self) -> bool:
        return self.has_after
