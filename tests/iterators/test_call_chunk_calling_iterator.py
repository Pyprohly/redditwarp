
from typing import Iterable

from redditwarp.iterators.call_chunk_calling_iterator import CallChunkCallingIterator
from redditwarp.iterators.call_chunk import CallChunk

class TestCallChunkChainingIterator:
    def test_chunks_attribute(self) -> None:
        it = [CallChunk(lambda x: x, 1)]
        ccci = CallChunkCallingIterator(it)
        assert list(ccci.get_chunk_iter()) == it

    def test_simple_iteration(self) -> None:
        it = [
            CallChunk(lambda x: x, 1),
            CallChunk(lambda x: x, 2),
            CallChunk(lambda x: x, 3),
        ]
        ccci = CallChunkCallingIterator(it)
        assert list(ccci) == [1,2,3]

    def test_exception_during_iteration(self) -> None:
        class ThrowOnFirstCallThenReturn:
            def __init__(self) -> None:
                self.call_count = 0
            def __call__(self, obj: int) -> int:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                return obj

        j = CallChunk(ThrowOnFirstCallThenReturn(), 2)
        it = [
            CallChunk(lambda x: x, 1),
            j,
            CallChunk(lambda x: x, 3),
        ]
        ccci = CallChunkCallingIterator(it)
        assert ccci.current is None
        assert next(ccci) == 1
        assert ccci.current is None
        try:
            next(ccci)
        except RuntimeError:
            pass
        assert ccci.current is j
        assert next(ccci) == 2
        assert ccci.current is None
        assert next(ccci) == 3
        assert ccci.current is None

    def test_current_is_setable(self) -> None:
        it: Iterable[CallChunk[int, int]] = ()
        ccci = CallChunkCallingIterator(it)
        assert list(ccci) == []
        ccci.current = CallChunk(lambda x: x, 8)
        assert list(ccci) == [8]
