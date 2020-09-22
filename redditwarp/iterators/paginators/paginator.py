
from __future__ import annotations
from typing import TypeVar, Sequence, Optional, Iterator

from abc import ABC, abstractmethod

T = TypeVar('T')

class Paginator(Iterator[Sequence[T]], ABC):
    def __init__(self) -> None:
        self.has_next = True
        self.cursor: Optional[str] = None
        self.limit: Optional[int] = None

    def __iter__(self) -> Iterator[Sequence[T]]:
        return self

    @abstractmethod
    def __next__(self) -> Sequence[T]:
        raise NotImplementedError

    def resume(self) -> None:
        self.has_next = True

    def reset(self) -> None:
        self.has_next = True
        self.cursor = None
