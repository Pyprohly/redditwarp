
from __future__ import annotations
from typing import TypeVar, Sequence, Optional, AsyncIterator

from abc import ABC, abstractmethod

T = TypeVar('T')

class AsyncPaginator(AsyncIterator[Sequence[T]], ABC):
    def __init__(self) -> None:
        self.limit: Optional[int] = None

    def __iter__(self) -> AsyncIterator[Sequence[T]]:
        return self

    async def __anext__(self) -> Sequence[T]:
        if not self.has_next():
            raise StopAsyncIteration
        return await self.next_result()

    @abstractmethod
    async def next_result(self) -> Sequence[T]:
        raise NotImplementedError

    async def next_page(self) -> Sequence[T]:
        return await self.next_result()

    @abstractmethod
    def has_next(self) -> bool:
        raise NotImplementedError
