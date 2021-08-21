
from __future__ import annotations
from typing import TypeVar, AsyncIterator, Iterator, Generic, Optional

from .async_paginator import AsyncPaginator

E = TypeVar('E')

class BasePaginatorChainingAsyncIterator(AsyncIterator[E]):
    def __init__(self, paginator: AsyncPaginator[E], amount: Optional[int] = None) -> None:
        self._paginator: AsyncPaginator[E] = paginator
        self.amount = amount
        self.count = 0
        self.current_iter: Iterator[E] = iter(())

    def __aiter__(self) -> AsyncIterator[E]:
        return self

    async def __anext__(self) -> E:
        if self.amount is None or self.count < self.amount:
            while True:
                for elem in self.current_iter:
                    self.count += 1
                    return elem

                if not self._paginator.next_available():
                    raise StopAsyncIteration

                if self._paginator.limit is not None and self.amount is not None:
                    remaining = self.amount - self.count
                    if remaining < self._paginator.limit:
                        self._paginator.limit = remaining

                it = await self._paginator.next_result()
                self.current_iter = iter(it)

        raise StopAsyncIteration

__bound = 'AsyncPaginator[E]'
TAsyncPaginator = TypeVar('TAsyncPaginator', bound=AsyncPaginator)  # type: ignore[type-arg]

class PaginatorChainingAsyncIterator(BasePaginatorChainingAsyncIterator[E], Generic[TAsyncPaginator, E]):
    def __init__(self, paginator: TAsyncPaginator, amount: Optional[int] = None) -> None:
        super().__init__(paginator, amount)
        self.paginator: TAsyncPaginator = paginator
