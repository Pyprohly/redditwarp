
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, AsyncIterator, Iterator, Generic, Optional
if TYPE_CHECKING:
    from .async_paginator import AsyncPaginator  # noqa: F401

from ..unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator

E = TypeVar('E')
P = TypeVar('P', bound='AsyncPaginator')

class PageChainingAsyncIterator(AsyncIterator[E], Generic[P, E]):
    @property
    def current_iter(self) -> Iterator[E]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[E]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, paginator: P, amount: Optional[int] = None) -> None:
        self.paginator = paginator
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
