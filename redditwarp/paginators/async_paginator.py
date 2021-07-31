
from __future__ import annotations
from typing import TypeVar, Sequence, Optional, Generic

from abc import ABC, abstractmethod

T = TypeVar('T')

class AsyncPaginator(Generic[T], ABC):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        self.limit: Optional[int] = limit

    @abstractmethod
    def next_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def next_result(self) -> Sequence[T]:
        raise NotImplementedError
