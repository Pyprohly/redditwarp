
from typing import Iterable

import pytest

from redditwarp.iterators.call_chunk_calling_async_iterator import CallChunkCallingAsyncIterator
from redditwarp.iterators.async_call_chunk import AsyncCallChunk

async def _f(x: int) -> int:
    return x

class TestCallChunkChainingIterator:
    @pytest.mark.asyncio
    async def test_current_iterator(self) -> None:
        it = [AsyncCallChunk(_f, 1)]
        ccci = CallChunkCallingAsyncIterator(it)
        assert list(ccci.get_chunking_iterator()) == it

    @pytest.mark.asyncio
    async def test_simple_iteration(self) -> None:
        it = [
            AsyncCallChunk(_f, 1),
            AsyncCallChunk(_f, 2),
            AsyncCallChunk(_f, 3),
        ]
        ccci = CallChunkCallingAsyncIterator(it)
        assert [i async for i in ccci] == [1,2,3]

    @pytest.mark.asyncio
    async def test_exception_during_iteration(self) -> None:
        class ThrowOnFirstCallThenReturn:
            def __init__(self) -> None:
                self.call_count = 0
            async def __call__(self, obj: int) -> int:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                return obj

        j = AsyncCallChunk(ThrowOnFirstCallThenReturn(), 2)
        it = [
            AsyncCallChunk(_f, 1),
            j,
            AsyncCallChunk(_f, 3),
        ]
        ccci = CallChunkCallingAsyncIterator(it)
        assert ccci.current_callable is None
        assert await ccci.__anext__() == 1
        assert ccci.current_callable is None
        try:
            await ccci.__anext__()
        except RuntimeError:
            pass
        assert ccci.current_callable is j
        assert await ccci.__anext__() == 2
        assert ccci.current_callable is None
        assert await ccci.__anext__() == 3
        assert ccci.current_callable is None

    @pytest.mark.asyncio
    async def test_current_is_setable(self) -> None:
        it: Iterable[AsyncCallChunk[int, int]] = ()
        ccci = CallChunkCallingAsyncIterator(it)
        assert [i async for i in ccci] == []
        ccci.current_callable = AsyncCallChunk(_f, 8)
        assert [i async for i in ccci] == [8]
