
from __future__ import annotations
from typing import TypeVar, Optional
from typing import Sequence  # noqa: F401

from .paginator import Paginator

P = TypeVar('P', bound='Sequence')

class BidirectionalPaginator(Paginator[P]):
    def __init__(self) -> None:
        super().__init__()
        self.forward = True
        self.back_cursor: Optional[str] = None
        self.has_prev = False
