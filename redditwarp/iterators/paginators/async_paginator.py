
from __future__ import annotations
from typing import TypeVar, Sequence, Optional, AsyncIterator

from abc import ABC, abstractmethod

T = TypeVar('T')

class AsyncPaginator(AsyncIterator[Sequence[T]], ABC):
    def __init__(self) -> None:
        self.limit = 0
        self.cursor: Optional[str] = None
        self.has_next = True

    def __aiter__(self) -> AsyncIterator[Sequence[T]]:
        return self

    @abstractmethod
    async def __anext__(self) -> Sequence[T]:
        raise NotImplementedError
