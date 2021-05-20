
from typing import List, Iterable

import pytest

from redditwarp.iterators.paginators.paginator_chaining_async_iterator import PaginatorChainingAsyncIterator
from redditwarp.iterators.paginators.async_paginator import AsyncPaginator

class IntIterableToAsyncPaginator(AsyncPaginator[int]):
    def __init__(self, it: Iterable[List[int]]) -> None:
        super().__init__()
        self._proceed = True
        self._itr = iter(it)

    async def next_result(self) -> List[int]:
        try:
            return next(self._itr)
        except StopIteration:
            self._proceed = False
            raise StopAsyncIteration

    def has_next(self) -> bool:
        return self._proceed


@pytest.mark.asyncio
async def test_simple_iteration() -> None:
    p = IntIterableToAsyncPaginator([
        [1],
        [2, 3],
        [4, 5, 6],
    ])
    pci: PaginatorChainingAsyncIterator[IntIterableToAsyncPaginator, int] = PaginatorChainingAsyncIterator(p)
    assert [i async for i in pci] == [1,2,3,4,5,6]

@pytest.mark.asyncio
async def test_current_iter() -> None:
    p = IntIterableToAsyncPaginator([
        [0, 1, 2],
        [3, 4],
    ])
    pci: PaginatorChainingAsyncIterator[IntIterableToAsyncPaginator, int] = PaginatorChainingAsyncIterator(p)

    assert await pci.__anext__() == 0
    assert list(pci.current_iter) == [1, 2]
    assert await pci.__anext__() == 3
    assert await pci.__anext__() == 4

    pci.current_iter = iter((8, 9))
    assert await pci.__anext__() == 8
    assert await pci.__anext__() == 9

@pytest.mark.asyncio
async def test_amount() -> None:
    p = IntIterableToAsyncPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci: PaginatorChainingAsyncIterator[IntIterableToAsyncPaginator, int] = PaginatorChainingAsyncIterator(p, 6)
    assert pci.amount == 6
    assert pci.count == 0
    assert await pci.__anext__() == 10
    assert pci.count == 1
    assert [i async for i in pci] == [20,30,40,50,60]
    assert pci.count == 6

    p = IntIterableToAsyncPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci = PaginatorChainingAsyncIterator(p)
    assert pci.amount is None
    assert [i async for i in pci] == [10,20,30,40,50,60,70,80]
    assert pci.count == 8

@pytest.mark.asyncio
async def test_efficient_pagination_limit() -> None:
    p = IntIterableToAsyncPaginator([
        list(range(100)),
        list(range(23)),
    ])
    p.limit = 100
    pci: PaginatorChainingAsyncIterator[IntIterableToAsyncPaginator, int] = PaginatorChainingAsyncIterator(p, 123)
    for _ in range(100):
        await pci.__anext__()
    assert pci.count == 100
    assert p.limit == 100
    await pci.__anext__()
    assert p.limit == 23
