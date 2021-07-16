
from __future__ import annotations
from typing import TypeVar, Sequence, Optional, Iterator

from abc import ABC, abstractmethod

T = TypeVar('T')

class Paginator(Iterator[Sequence[T]], ABC):
    def __init__(self) -> None:
        self.limit: Optional[int] = None

    def __iter__(self) -> Iterator[Sequence[T]]:
        return self

    def __next__(self) -> Sequence[T]:
        if not self.has_next():
            raise StopIteration
        return self.next_result()

    @abstractmethod
    def next_result(self) -> Sequence[T]:
        raise NotImplementedError

    @abstractmethod
    def has_next(self) -> bool:
        raise NotImplementedError
