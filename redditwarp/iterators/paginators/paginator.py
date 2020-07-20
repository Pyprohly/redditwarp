
from __future__ import annotations
from typing import TypeVar, Sequence, Optional, Iterator

from abc import ABC, abstractmethod

T = TypeVar('T')

class Paginator(Iterator[Sequence[T]], ABC):
    def __init__(self) -> None:
        self.limit = 0
        self.cursor: Optional[str] = None
        self.has_next = True

    def __iter__(self) -> Iterator[Sequence[T]]:
        return self

    @abstractmethod
    def __next__(self) -> Sequence[T]:
        raise NotImplementedError
