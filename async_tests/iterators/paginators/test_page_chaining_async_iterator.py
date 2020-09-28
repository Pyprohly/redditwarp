
from typing import List

import pytest

from redditwarp.iterators.paginators.page_chaining_async_iterator import PageChainingAsyncIterator
from redditwarp.iterators.paginators.async_paginator import AsyncPaginator


@pytest.mark.asyncio
async def test_simple_iteration() -> None:
    class MyAsyncPaginator(AsyncPaginator[int]):
        def __init__(self) -> None:
            super().__init__()
            self._itr = iter([
                [1],
                [2, 3],
                [4, 5, 6],
            ])

        async def __anext__(self) -> List[int]:
            try:
                return next(self._itr)
            except StopIteration:
                raise StopAsyncIteration

    p = MyAsyncPaginator()
    pci: PageChainingAsyncIterator[MyAsyncPaginator, int] = PageChainingAsyncIterator(p)
    assert [i async for i in pci] == [1,2,3,4,5,6]

@pytest.mark.asyncio
async def test_current_iter() -> None:
    class MyAsyncPaginator(AsyncPaginator[int]):
        def __init__(self) -> None:
            super().__init__()
            self._itr = iter([
                [0, 1, 2],
                [3, 4],
            ])

        async def __anext__(self) -> List[int]:
            try:
                return next(self._itr)
            except StopIteration:
                raise StopAsyncIteration

    pci: PageChainingAsyncIterator[MyAsyncPaginator, int] = PageChainingAsyncIterator(MyAsyncPaginator())

    assert await pci.__anext__() == 0
    assert list(pci.current_iter) == [1, 2]
    assert await pci.__anext__() == 3
    assert await pci.__anext__() == 4

    pci.current_iter = iter((8, 9))
    assert await pci.__anext__() == 8
    assert await pci.__anext__() == 9

@pytest.mark.asyncio
async def test_amount() -> None:
    class MyAsyncPaginator(AsyncPaginator[int]):
        def __init__(self) -> None:
            super().__init__()
            self._itr = iter([
                [10, 20, 30, 40],
                [50, 60, 70, 80],
            ])

        async def __anext__(self) -> List[int]:
            try:
                return next(self._itr)
            except StopIteration:
                raise StopAsyncIteration

    pci: PageChainingAsyncIterator[MyAsyncPaginator, int] = PageChainingAsyncIterator(MyAsyncPaginator(), 6)
    assert pci.amount == 6
    assert pci.count == 0
    assert await pci.__anext__() == 10
    assert pci.count == 1
    assert [i async for i in pci] == [20,30,40,50,60]
    assert pci.count == 6

    pci = PageChainingAsyncIterator(MyAsyncPaginator())
    assert pci.amount is None
    assert [i async for i in pci] == [10,20,30,40,50,60,70,80]
    assert pci.count == 8

@pytest.mark.asyncio
async def test_efficient_pagination_limit() -> None:
    class MyAsyncPaginator(AsyncPaginator[int]):
        def __init__(self) -> None:
            super().__init__()
            self._itr = iter([
                list(range(100)),
                list(range(23)),
            ])

        async def __anext__(self) -> List[int]:
            try:
                return next(self._itr)
            except StopIteration:
                raise StopAsyncIteration

    p = MyAsyncPaginator()
    p.limit = 100
    pci: PageChainingAsyncIterator[MyAsyncPaginator, int] = PageChainingAsyncIterator(p, 123)
    for _ in range(100):
        await pci.__anext__()
    assert pci.count == 100
    assert p.limit == 100
    await pci.__anext__()
    assert p.limit == 23
