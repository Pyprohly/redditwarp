
from typing import Sequence

import pytest

from redditwarp.paginators.paginator_chaining_async_iterator import PaginatorChainingAsyncIterator
from redditwarp.paginators.async_paginator import AsyncPaginator

class MyAsyncPaginator(AsyncPaginator[int]):
    def __init__(self, seq: Sequence[Sequence[int]]) -> None:
        super().__init__()
        self.seq = seq
        self.index = -1
        self.proceed = True

    def next_available(self) -> bool:
        return self.proceed

    async def fetch_next_result(self) -> Sequence[int]:
        self.index += 1
        if self.index >= len(self.seq) - 1:
            self.proceed = False
        return self.seq[self.index]


@pytest.mark.asyncio
async def test_simple_iteration() -> None:
    p = MyAsyncPaginator([
        [1],
        [2, 3],
        [4, 5, 6],
    ])
    pci: PaginatorChainingAsyncIterator[MyAsyncPaginator, int] = PaginatorChainingAsyncIterator(p)
    assert [i async for i in pci] == [1,2,3,4,5,6]

@pytest.mark.asyncio
async def test_current_iter() -> None:
    p = MyAsyncPaginator([
        [0, 1, 2],
        [3, 4],
    ])
    pci: PaginatorChainingAsyncIterator[MyAsyncPaginator, int] = PaginatorChainingAsyncIterator(p)

    assert await pci.__anext__() == 0
    assert list(pci.current_iter) == [1, 2]
    assert await pci.__anext__() == 3
    assert await pci.__anext__() == 4

    pci.current_iter = iter((8, 9))
    assert await pci.__anext__() == 8
    assert await pci.__anext__() == 9

@pytest.mark.asyncio
async def test_amount() -> None:
    p = MyAsyncPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci: PaginatorChainingAsyncIterator[MyAsyncPaginator, int] = PaginatorChainingAsyncIterator(p, 6)
    assert pci.amount == 6
    assert pci.count == 0
    assert await pci.__anext__() == 10
    assert pci.count == 1
    assert [i async for i in pci] == [20,30,40,50,60]
    assert pci.count == 6

    p = MyAsyncPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci = PaginatorChainingAsyncIterator(p)
    assert pci.amount is None
    assert [i async for i in pci] == [10,20,30,40,50,60,70,80]
    assert pci.count == 8

@pytest.mark.asyncio
async def test_efficient_pagination_limit() -> None:
    p = MyAsyncPaginator([
        list(range(100)),
        list(range(23)),
    ])
    p.limit = 100
    pci: PaginatorChainingAsyncIterator[MyAsyncPaginator, int] = PaginatorChainingAsyncIterator(p, 123)
    for _ in range(100):
        await pci.__anext__()
    assert pci.count == 100
    assert p.limit == 100
    await pci.__anext__()
    assert p.limit == 23
