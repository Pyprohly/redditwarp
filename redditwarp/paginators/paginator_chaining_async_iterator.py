
from __future__ import annotations
from typing import TypeVar, AsyncIterator, Iterator, Generic, Optional

from .async_paginator import AsyncPaginator

E = TypeVar('E')

class PaginatorChainingAsyncIterator(AsyncIterator[E]):
    def __init__(self, paginator: AsyncPaginator[E], amount: Optional[int] = None) -> None:
        self._pgr: AsyncPaginator[E] = paginator
        self.remaining: Optional[int] = amount
        self.current_iter: Iterator[E] = iter(())

    def __aiter__(self) -> AsyncIterator[E]:
        return self

    async def __anext__(self) -> E:
        if self.remaining is None or self.remaining > 0:
            while True:
                for elem in self.current_iter:
                    if self.remaining is not None:
                        self.remaining -= 1
                    return elem

                if not self._pgr.next_available():
                    raise StopAsyncIteration

                if self._pgr.limit is not None and self.remaining is not None:
                    if self.remaining < self._pgr.limit:
                        self._pgr.limit = self.remaining

                it = await self._pgr.fetch_next()
                self.current_iter = iter(it)

        raise StopAsyncIteration



__bound = 'AsyncPaginator[E]'
TAsyncPaginator = TypeVar('TAsyncPaginator', bound=AsyncPaginator)  # type: ignore[type-arg]

class PaginatorChainingAsyncIteratorAggregate(PaginatorChainingAsyncIterator[E], Generic[TAsyncPaginator, E]):
    def __init__(self, paginator: TAsyncPaginator, amount: Optional[int] = None) -> None:
        super().__init__(paginator, amount)
        self.__paginator: TAsyncPaginator = paginator

    def get_paginator(self) -> TAsyncPaginator:
        return self.__paginator
