
from typing import TypeVar, Iterable, AsyncIterable, Callable, Awaitable

import asyncio

import pytest  # type: ignore[import]

from redditwarp.util.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator

T = TypeVar('T')

async def A(iterable: Iterable[T]) -> AsyncIterable[T]:
    for i in iterable:
        yield i

@pytest.mark.asyncio
async def test_call_chunks_attrib() -> None:
    async def f() -> AsyncIterable[int]: return A([1])
    it: AsyncIterable[Callable[[], Awaitable[AsyncIterable[int]]]] = A([f])
    cci = CallChunkChainingAsyncIterator(it)
    assert cci.call_chunks is it

@pytest.mark.asyncio
async def test_simple_iteration() -> None:
    async def f1() -> AsyncIterable[int]: return A([1])
    async def f2() -> AsyncIterable[int]: return A([2, 3])
    async def f3() -> AsyncIterable[int]: return A([4, 5, 6])
    it = A([
        f1,
        f2,
        f3,
    ])
    cci = CallChunkChainingAsyncIterator(it)
    assert [i async for i in cci] == [1,2,3,4,5,6]

@pytest.mark.asyncio
async def test_current_iter() -> None:
    async def f1() -> AsyncIterable[int]: return A([0, 1, 2])
    async def f2() -> AsyncIterable[int]: return A([3, 4])
    it = A([f1, f2])
    cci = CallChunkChainingAsyncIterator(it)

    assert await cci.__anext__() == 0
    assert [i async for i in cci.current_iter] == [1, 2]
    assert await cci.__anext__() == 3
    assert await cci.__anext__() == 4

    cci.current_iter = A((8, 9)).__aiter__()
    assert await cci.__anext__() == 8
    assert await cci.__anext__() == 9

@pytest.mark.asyncio
async def test_exception_during_iteration() -> None:
    class throw_on_first_call_then_return:
        def __init__(self) -> None:
            self.call_count = 0
        def __call__(self) -> Awaitable[AsyncIterable[int]]:
            self.call_count += 1
            if self.call_count == 1:
                raise RuntimeError
            fut: asyncio.Future[AsyncIterable[int]] = asyncio.Future()
            fut.set_result(A([2]))
            return fut

    j = throw_on_first_call_then_return()
    async def f1() -> AsyncIterable[int]: return A([1])
    async def f2() -> AsyncIterable[int]: return A([3])
    it: AsyncIterable[Callable[[], Awaitable[AsyncIterable[int]]]] = A([
        f1,
        j,
        f2,
    ])
    cci = CallChunkChainingAsyncIterator(it)
    assert cci.current_callable is None
    assert await cci.__anext__() == 1
    assert cci.current_callable is None
    try:
        await cci.__anext__()
    except RuntimeError:
        pass
    assert cci.current_callable is j
    assert await cci.__anext__() == 2
    assert cci.current_callable is None
    assert await cci.__anext__() == 3

@pytest.mark.asyncio
async def test_current_callable_is_setable() -> None:
    async def f1() -> AsyncIterable[int]: return A(())
    it: AsyncIterable[Callable[[], Awaitable[AsyncIterable[int]]]] = A([f1])
    cci = CallChunkChainingAsyncIterator(it)
    assert [i async for i in cci] == []
    async def f2() -> AsyncIterable[int]: return A((1,2,3))
    cci.current_callable = f2
    assert [i async for i in cci] == [1,2,3]
