
from __future__ import annotations
from typing import TypeVar, AsyncIterator, Iterator, Generic, Optional

from .async_paginator import AsyncPaginator

E = TypeVar('E')

class PaginatorChainingAsyncIterator(AsyncIterator[E]):
    def __init__(self, paginator: AsyncPaginator[E], amount: Optional[int] = None) -> None:
        self._pgr: AsyncPaginator[E] = paginator
        self.remaining = amount
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

                it = await self._pgr.next_result()
                self.current_iter = iter(it)

        raise StopAsyncIteration

__bound = 'AsyncPaginator[E]'
TAsyncPaginator = TypeVar('TAsyncPaginator', bound=AsyncPaginator)  # type: ignore[type-arg]

class PaginatorChainingAsyncWrapper(AsyncIterator[E], Generic[TAsyncPaginator, E]):
    def __init__(self, chainer: PaginatorChainingAsyncIterator[E], paginator: TAsyncPaginator) -> None:
        self.chainer: PaginatorChainingAsyncIterator[E] = chainer
        self.paginator: TAsyncPaginator = paginator

    def __aiter__(self) -> AsyncIterator[E]:
        return self.chainer.__aiter__()

    async def __anext__(self) -> E:
        return await self.chainer.__anext__()
