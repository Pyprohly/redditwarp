
from typing import TypeVar, Iterable, AsyncIterable, Sequence

import pytest

from redditwarp.iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from redditwarp.iterators.call_chunk_ASYNC import CallChunk

T = TypeVar('T')

async def to_async_iterable(iterable: Iterable[T]) -> AsyncIterable[T]:
    for i in iterable:
        yield i

class TestCallChunkChainingAsyncIterator:
    @pytest.mark.asyncio
    async def test_chunks_attribute(self) -> None:
        async def _f(x: Sequence[int]) -> Sequence[int]: return x
        it = [CallChunk(_f, [1])]
        cci = CallChunkChainingAsyncIterator(it)
        assert cci.chunks is it

    @pytest.mark.asyncio
    async def test_simple_iteration(self) -> None:
        async def _f(x: Sequence[int]) -> Sequence[int]: return x
        it = [
            CallChunk(_f, [1]),
            CallChunk(_f, [2, 3]),
            CallChunk(_f, [4, 5, 6]),
        ]
        cci = CallChunkChainingAsyncIterator(it)
        assert [i async for i in cci] == [1,2,3,4,5,6]

    @pytest.mark.asyncio
    async def test_current_iter(self) -> None:
        async def _f(x: Sequence[int]) -> Sequence[int]: return x
        it = [CallChunk(_f, [0, 1, 2]), CallChunk(_f, [3, 4])]
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
        async def _f(x: Sequence[int]) -> Sequence[int]: return x

        class throw_on_first_call_then_return:
            def __init__(self) -> None:
                self.call_count = 0
            async def __call__(self, seq: Sequence[int]) -> Sequence[int]:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                return seq

        j = CallChunk(throw_on_first_call_then_return(), [2])
        it = [
            CallChunk(_f, [1]),
            j,
            CallChunk(_f, [3]),
        ]
        cci = CallChunkChainingAsyncIterator(it)
        assert cci.current is None
        assert await cci.__anext__() == 1
        assert cci.current is None
        try:
            await cci.__anext__()
        except RuntimeError:
            pass
        assert cci.current is j
        assert await cci.__anext__() == 2
        assert cci.current is None
        assert await cci.__anext__() == 3

    @pytest.mark.asyncio
    async def test_current_is_setable(self) -> None:
        async def _f(x: Sequence[int]) -> Sequence[int]: return x
        it: Iterable[CallChunk[int, int]] = []
        cci = CallChunkChainingAsyncIterator(it)
        assert [i async for i in cci] == []
        cci.current = CallChunk(_f, [1, 2, 3])
        assert [i async for i in cci] == [1, 2, 3]
