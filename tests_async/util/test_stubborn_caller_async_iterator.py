
from typing import TypeVar, Iterable, AsyncIterable, Callable, Awaitable

import asyncio

import pytest  # type: ignore[import]

from redditwarp.util.stubborn_caller_async_iterator import StubbornCallerAsyncIterator

T = TypeVar('T')

async def A(iterable: Iterable[T]) -> AsyncIterable[T]:
    for i in iterable:
        yield i

@pytest.mark.asyncio
async def test_iteration() -> None:
    async def f1() -> int: return 1
    async def f2() -> int: return 7
    async def f3() -> int: return 2
    async def f4() -> int: return 8
    async def f5() -> int: return 5
    it: AsyncIterable[Callable[[], Awaitable[int]]] = A([
        f1,
        f2,
        f3,
        f4,
        f5,
    ])
    sci = StubbornCallerAsyncIterator(it)
    assert [i async for i in sci] == [1, 7, 2, 8, 5]
    it = A([])
    assert [i async for i in StubbornCallerAsyncIterator(it)] == []

@pytest.mark.asyncio
async def test_exception_during_iteration() -> None:
    class throw_on_first_call_then_return:
        def __init__(self) -> None:
            self.call_count = 0
        def __call__(self) -> Awaitable[int]:
            self.call_count += 1
            if self.call_count == 1:
                raise RuntimeError
            fut: asyncio.Future[int] = asyncio.Future()
            fut.set_result(3)
            return fut

    j = throw_on_first_call_then_return()
    async def f1() -> int: return 1
    async def f2() -> int: return 2
    async def f3() -> int: return 4
    async def f4() -> int: return 5
    it: AsyncIterable[Callable[[], Awaitable[int]]] = A([
        f1,
        f2,
        j,
        f3,
        f4,
    ])
    sci = StubbornCallerAsyncIterator(it)
    assert await sci.__anext__() == 1
    assert await sci.__anext__() == 2
    assert sci.current is None
    try:
        await sci.__anext__()
    except RuntimeError:
        pass
    assert sci.current is j
    assert await sci.__anext__() == 3
    assert sci.current is None
    assert await sci.__anext__() == 4
    assert await sci.__anext__() == 5
