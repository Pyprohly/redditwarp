
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
        async def f() -> AsyncIterable[int]: return A([1])
        it: AsyncIterable[Callable[[], Awaitable[AsyncIterable[int]]]] = A([f])
        cci = CallChunkChainingAsyncIterator(it)
        assert cci.call_chunks is it

    @pytest.mark.asyncio
    async def test_simple_iteration(self) -> None:
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
    async def test_current_iter(self) -> None:
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
    async def test_exception_during_iteration(self) -> None:
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
    async def test_current_callable_is_setable(self) -> None:
        async def f1() -> AsyncIterable[int]: return A(())
        it: AsyncIterable[Callable[[], Awaitable[AsyncIterable[int]]]] = A([f1])
        cci = CallChunkChainingAsyncIterator(it)
        assert [i async for i in cci] == []
        async def f2() -> AsyncIterable[int]: return A((1,2,3))
        cci.current_callable = f2
        assert [i async for i in cci] == [1,2,3]

class TestChunkSizeAdjustableCallChunkChainingAsyncIterator:
    @pytest.mark.asyncio
    async def test_changing_chunk_size(self) -> None:
        it = list(range(10))
        ci: Iterable[Iterable[int]] = ChunkingIterator(it, 2)
        ##Iterable[Iterable[T]]
        def f(x: AsyncIterable[int]) -> Callable[[], Awaitable[AsyncIterable[int]]]:
            async def _f() -> AsyncIterable[int]:
                return x
            return _f

        async def async_map(
            f: Callable[[TSource], Awaitable[AsyncIterable[TResult]]],
            it: AsyncIterable[TSource],
        ) -> AsyncIterable[Awaitable[AsyncIterable[TResult]]]:
            async for i in it:
                yield f(i)

        it2: Iterable[AsyncIterable[int]] = await async_map(A, ci)
        it3 = await async_map(A, it2)
        it4 = await async_map(f, it3)
        reveal_type(it4)
        ##AsyncIterable[Callable[[], Awaitable[AsyncIterable[T]]]]
        ccci = ChunkSizeAdjustableCallChunkChainingAsyncIterator(it4, ci)
        assert ccci.chunk_size == 2
        call_chunks = iter(ccci.call_chunks)
        assert tuple(next(call_chunks)()) == (0, 1)
        ccci.chunk_size = 5
        assert tuple(next(call_chunks)()) == (2,3,4,5,6)
