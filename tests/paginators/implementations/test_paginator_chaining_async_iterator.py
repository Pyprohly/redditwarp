
from typing import Sequence

import pytest

from redditwarp.pagination.paginator_chaining_async_iterator import PaginatorChainingAsyncIterator
from redditwarp.pagination.async_paginator import AsyncPaginator

class MyAsyncPaginator(AsyncPaginator[int]):
    def __init__(self, seq: Sequence[Sequence[int]]) -> None:
        super().__init__()
        self._itr = iter(seq)

    async def fetch(self) -> Sequence[int]:
        return next(self._itr, [])


@pytest.mark.asyncio
async def test_simple_iteration() -> None:
    p = MyAsyncPaginator([
        [1],
        [2, 3],
        [4, 5, 6],
    ])
    pci: PaginatorChainingAsyncIterator[int] = PaginatorChainingAsyncIterator(p)
    assert [i async for i in pci] == [1,2,3,4,5,6]

@pytest.mark.asyncio
async def test_current_iterator() -> None:
    p = MyAsyncPaginator([
        [0, 1, 2],
        [3, 4],
    ])
    pci: PaginatorChainingAsyncIterator[int] = PaginatorChainingAsyncIterator(p)

    assert await pci.__anext__() == 0
    assert list(pci.current_iterator) == [1, 2]
    assert await pci.__anext__() == 3
    assert await pci.__anext__() == 4

    pci.current_iterator = iter((8, 9))
    assert await pci.__anext__() == 8
    assert await pci.__anext__() == 9

@pytest.mark.asyncio
async def test_remaining() -> None:
    p = MyAsyncPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci: PaginatorChainingAsyncIterator[int] = PaginatorChainingAsyncIterator(p, 6)
    assert pci.remaining == 6
    assert await pci.__anext__() == 10
    assert pci.remaining == 5
    assert [i async for i in pci] == [20,30,40,50,60]
    assert pci.remaining == 0

    p = MyAsyncPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci = PaginatorChainingAsyncIterator(p)
    assert pci.remaining is None
    assert [i async for i in pci] == [10,20,30,40,50,60,70,80]
    assert pci.remaining is None

@pytest.mark.asyncio
async def test_efficient_pagination_limit() -> None:
    p = MyAsyncPaginator([
        list(range(100)),
        list(range(23)),
    ])
    p.limit = 100
    pci: PaginatorChainingAsyncIterator[int] = PaginatorChainingAsyncIterator(p, 123)
    for _ in range(100):
        await pci.__anext__()
    assert pci.remaining == 23
    assert p.limit == 100
    await pci.__anext__()
    assert p.limit == 23
