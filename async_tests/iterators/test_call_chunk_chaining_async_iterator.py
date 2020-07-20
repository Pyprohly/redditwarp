
from typing import TypeVar, Iterable, AsyncIterable, Callable, Awaitable

import asyncio

import pytest  # type: ignore[import]

from redditwarp.iterators.call_chunk_chaining_async_iterator import (
    CallChunkChainingAsyncIterator,
    ChunkSizeAdjustableCallChunkChainingAsyncIterator,
)
from redditwarp.iterators.chunking_iterator import ChunkingIterator

T = TypeVar('T')
TSource = TypeVar('TSource')
TResult = TypeVar('TResult')

async def A(iterable: Iterable[T]) -> AsyncIterable[T]:
    for i in iterable:
        yield i

class TestCallChunkChainingAsyncIterator:
    @pytest.mark.asyncio
    async def test_call_chunks_attrib(self) -> None:
        async def f() -> Iterable[int]: return [1]
        it: Iterable[Callable[[], Awaitable[Iterable[int]]]] = [f]
        cci = CallChunkChainingAsyncIterator(it)
        assert cci.call_chunks is it

    @pytest.mark.asyncio
    async def test_simple_iteration(self) -> None:
        async def f1() -> Iterable[int]: return [1]
        async def f2() -> Iterable[int]: return [2, 3]
        async def f3() -> Iterable[int]: return [4, 5, 6]
        it = [
            f1,
            f2,
            f3,
        ]
        cci = CallChunkChainingAsyncIterator(it)
        assert [i async for i in cci] == [1,2,3,4,5,6]

    @pytest.mark.asyncio
    async def test_current_iter(self) -> None:
        async def f1() -> Iterable[int]: return [0, 1, 2]
        async def f2() -> Iterable[int]: return [3, 4]
        it = [f1, f2]
        cci = CallChunkChainingAsyncIterator(it)

        assert await cci.__anext__() == 0
        assert list(cci.current_iter) == [1, 2]
        assert await cci.__anext__() == 3
        assert await cci.__anext__() == 4

        cci.current_iter = iter((8, 9))
        assert await cci.__anext__() == 8
        assert await cci.__anext__() == 9

    @pytest.mark.asyncio
    async def test_exception_during_iteration(self) -> None:
        class throw_on_first_call_then_return:
            def __init__(self) -> None:
                self.call_count = 0
            def __call__(self) -> Awaitable[Iterable[int]]:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                fut: asyncio.Future[Iterable[int]] = asyncio.Future()
                fut.set_result([2])
                return fut

        j = throw_on_first_call_then_return()
        async def f1() -> Iterable[int]: return [1]
        async def f2() -> Iterable[int]: return [3]
        it: Iterable[Callable[[], Awaitable[Iterable[int]]]] = [
            f1,
            j,
            f2,
        ]
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
    async def test_current_callable_is_setable(self) -> None:
        async def f1() -> Iterable[int]: return ()
        it: Iterable[Callable[[], Awaitable[Iterable[int]]]] = [f1]
        cci = CallChunkChainingAsyncIterator(it)
        assert [i async for i in cci] == []
        async def f2() -> Iterable[int]: return (1,2,3)
        cci.current_callable = f2
        assert [i async for i in cci] == [1,2,3]

class TestChunkSizeAdjustableCallChunkChainingIterator:
    @pytest.mark.asyncio
    async def test_changing_chunk_size(self) -> None:
        it = list(range(10))
        ci = ChunkingIterator(it, 2)

        def f(x: Iterable[int]) -> Callable[[], Awaitable[Iterable[int]]]:
            async def _f() -> Iterable[int]:
                return x
            return _f

        it2 = map(f, ci)
        ccci = ChunkSizeAdjustableCallChunkChainingAsyncIterator(it2, ci)
        assert ccci.chunk_size == 2
        call_chunks = iter(ccci.call_chunks)
        assert tuple(await next(call_chunks)()) == (0, 1)
        ccci.chunk_size = 5
        assert tuple(await next(call_chunks)()) == (2,3,4,5,6)
