
from typing import Iterable, Sequence

from redditwarp.iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from redditwarp.iterators.call_chunk_SYNC import CallChunk

class TestCallChunkChainingIterator:
    def test_chunks_attribute(self) -> None:
        it = [CallChunk(lambda x: x, [1])]
        ccci = CallChunkChainingIterator(it)
        assert ccci.chunks is it

    def test_simple_iteration(self) -> None:
        it = [
            CallChunk(lambda x: x, [1]),
            CallChunk(lambda x: x, [2, 3]),
            CallChunk(lambda x: x, [4, 5, 6]),
        ]
        ccci = CallChunkChainingIterator(it)
        assert list(ccci) == [1,2,3,4,5,6]

    def test_current_iter(self) -> None:
        it = [
            CallChunk(lambda x: x, [0, 1, 2]),
            CallChunk(lambda x: x, [3, 4]),
        ]
        ccci = CallChunkChainingIterator(it)

        assert next(ccci) == 0
        assert list(ccci.current_iter) == [1, 2]
        assert next(ccci) == 3
        assert next(ccci) == 4

        ccci.current_iter = iter((8, 9))
        assert next(ccci) == 8
        assert next(ccci) == 9

    def test_exception_during_iteration(self) -> None:
        class throw_on_first_call_then_return:
            def __init__(self) -> None:
                self.call_count = 0
            def __call__(self, seq: Sequence[int]) -> Sequence[int]:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                return seq

        j = CallChunk(throw_on_first_call_then_return(), [2])
        it = [
            CallChunk(lambda x: x, [1]),
            j,
            CallChunk(lambda x: x, [3]),
        ]
        ccci = CallChunkChainingIterator(it)
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

    def test_current_is_setable(self) -> None:
        it: Iterable[CallChunk[int, int]] = ()
        ccci = CallChunkChainingIterator(it)
        assert list(ccci) == []
        ccci.current = CallChunk(lambda x: x, [1, 2, 3])
        assert list(ccci) == [1, 2, 3]
