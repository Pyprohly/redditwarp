
from typing import Iterable, Sequence, Callable, Awaitable

import pytest

from redditwarp.iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from redditwarp.iterators.async_call_chunk import AsyncCallChunk, TInput, TOutput
from redditwarp.iterators.stubborn_caller_async_iterator import StubbornCallerAsyncIterator

def new_call_chunk_of_sequences(
    operation: Callable[[Sequence[TInput]], Awaitable[Sequence[TOutput]]],
    data: Sequence[TInput],
) -> AsyncCallChunk[Sequence[TInput], Sequence[TOutput]]:
    return AsyncCallChunk(operation, data)

async def _f(x: Sequence[int]) -> Sequence[int]:
    return x

class TestCallChunkChainingAsyncIterator:
    @pytest.mark.asyncio
    async def test_chunks_attribute(self) -> None:
        it = [new_call_chunk_of_sequences(_f, [1])]
        ccci = CallChunkChainingAsyncIterator(it)
        assert list(ccci.get_chunk_iter()) == it

    @pytest.mark.asyncio
    async def test_simple_iteration(self) -> None:
        it = [
            new_call_chunk_of_sequences(_f, [1]),
            new_call_chunk_of_sequences(_f, [2, 3]),
            new_call_chunk_of_sequences(_f, [4, 5, 6]),
        ]
        ccci = CallChunkChainingAsyncIterator(it)
        assert [i async for i in ccci] == [1,2,3,4,5,6]

    @pytest.mark.asyncio
    async def test_current_iter(self) -> None:
        it = [new_call_chunk_of_sequences(_f, [0, 1, 2]), new_call_chunk_of_sequences(_f, [3, 4])]
        ccci = CallChunkChainingAsyncIterator(it)

        assert await ccci.__anext__() == 0
        assert list(ccci.current_iter) == [1, 2]
        assert await ccci.__anext__() == 3
        assert await ccci.__anext__() == 4

        ccci.current_iter = iter((8, 9))
        assert await ccci.__anext__() == 8
        assert await ccci.__anext__() == 9

    @pytest.mark.asyncio
    async def test_exception_during_iteration(self) -> None:
        class throw_on_first_call_then_return:
            def __init__(self) -> None:
                self.call_count = 0
            async def __call__(self, seq: Sequence[int]) -> Sequence[int]:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                return seq

        j = new_call_chunk_of_sequences(throw_on_first_call_then_return(), [2])
        it = [
            new_call_chunk_of_sequences(_f, [1]),
            j,
            new_call_chunk_of_sequences(_f, [3]),
        ]
        ccci = CallChunkChainingAsyncIterator(it)
        sci = ccci.get_caller_iter()
        assert isinstance(sci, StubbornCallerAsyncIterator)
        assert sci.current is None
        assert await ccci.__anext__() == 1
        assert sci.current is None
        try:
            await ccci.__anext__()
        except RuntimeError:
            pass
        assert sci.current is j
        assert await ccci.__anext__() == 2
        assert sci.current is None
        assert await ccci.__anext__() == 3
        assert sci.current is None

    @pytest.mark.asyncio
    async def test_current_is_setable(self) -> None:
        it: Iterable[AsyncCallChunk[Sequence[int], Sequence[int]]] = []
        ccci = CallChunkChainingAsyncIterator(it)
        sci = ccci.get_caller_iter()
        assert isinstance(sci, StubbornCallerAsyncIterator)
        assert [i async for i in ccci] == []
        sci.current = new_call_chunk_of_sequences(_f, [1, 2, 3])
        assert [i async for i in ccci] == [1, 2, 3]
