
from __future__ import annotations
from typing import TypeVar, AsyncIterator, Iterator, Generic, Optional

from .async_paginator import AsyncPaginator

E = TypeVar('E')
AsyncPaginator_E = AsyncPaginator[E]
P = TypeVar('P', bound=AsyncPaginator_E)  # type: ignore[type-arg]

class PageChainingAsyncIterator(AsyncIterator[E], Generic[P, E]):
    def __init__(self, paginator: P, amount: Optional[int] = None) -> None:
        self.paginator = paginator
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

                if self.paginator.limit is not None and self.amount is not None:
                    remaining = self.amount - self.count
                    if remaining < self.paginator.limit:
                        self.paginator.limit = remaining

                it = await self.paginator.__anext__()
                self.current_iter = iter(it)

        raise StopAsyncIteration
