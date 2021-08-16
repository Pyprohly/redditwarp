
from __future__ import annotations
from typing import TypeVar, Sequence, Optional, Generic

from abc import ABC, abstractmethod

T = TypeVar('T')

class Paginator(Generic[T], ABC):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        self.limit: Optional[int] = limit

    @abstractmethod
    def next_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch_next_result(self) -> Sequence[T]:
        raise NotImplementedError
