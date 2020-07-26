
from __future__ import annotations
from typing import TypeVar, AsyncIterator, Iterator, Generic, Optional

from .async_paginator import AsyncPaginator
from ..unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator

E = TypeVar('E')

class PageChainingAsyncIterator(AsyncIterator[E]):
    @property
    def current_iter(self) -> Iterator[E]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[E]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, paginator: AsyncPaginator, amount: Optional[int] = None) -> None:
        self.amount = amount
        self.count = 0
        self._chain_iter: UnfalteringChainingAsyncIterator[E] = UnfalteringChainingAsyncIterator(paginator)

    def __aiter__(self) -> AsyncIterator[E]:
        return self

    async def __anext__(self) -> E:
        if self.amount is None or self.count < self.amount:
            el = await self._chain_iter.__anext__()
            self.count += 1
            return el
        raise StopAsyncIteration

AsyncPaginator_E = AsyncPaginator[E]
P = TypeVar('P', bound=AsyncPaginator_E)

class PaginatorKeepingPageChainingAsyncIterator(PageChainingAsyncIterator[E], Generic[P, E]):
    def __init__(self, paginator: P, amount: Optional[int]) -> None:
        super().__init__(paginator, amount)
        self.paginator = paginator
