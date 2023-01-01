
from __future__ import annotations
from typing import TypeVar, AsyncIterator, Iterator, Generic, Optional, Sequence

from .async_paginator import AsyncPaginator

E = TypeVar('E')

class PaginatorChainingAsyncIterator(AsyncIterator[E]):
    def __init__(self, paginator: AsyncPaginator[E], amount: Optional[int] = None) -> None:
        self._paginator: AsyncPaginator[E] = paginator
        self._paginator_iterator: AsyncIterator[Sequence[E]] = paginator.__aiter__()
        self.remaining: Optional[int] = amount
        self.current_iterator: Iterator[E] = iter(())

    def __aiter__(self) -> AsyncIterator[E]:
        return self

    async def __anext__(self) -> E:
        limit = self._paginator.limit
        remaining = self.remaining
        if remaining is None or remaining > 0:
            while True:
                for elem in self.current_iterator:
                    if self.remaining is not None:
                        self.remaining -= 1
                    return elem

                if (limit is not None and remaining is not None) and limit > remaining:
                    self._paginator.limit = remaining

                it = await self._paginator_iterator.__anext__()
                self.current_iterator = iter(it)

        raise StopAsyncIteration



__bound = 'AsyncPaginator[E]'
TAsyncPaginator = TypeVar('TAsyncPaginator', bound=AsyncPaginator)  # type: ignore[type-arg]

class ImpartedPaginatorChainingAsyncIterator(PaginatorChainingAsyncIterator[E], Generic[TAsyncPaginator, E]):
    def __init__(self, paginator: TAsyncPaginator, amount: Optional[int] = None) -> None:
        super().__init__(paginator, amount)
        self.__paginator: TAsyncPaginator = paginator

    def get_paginator(self) -> TAsyncPaginator:
        return self.__paginator
