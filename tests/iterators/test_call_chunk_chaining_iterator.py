
from typing import Callable, Iterable

from redditwarp.iterators.call_chunk_chaining_iterator import (
    CallChunkChainingIterator,
    ChunkSizeAdjustableCallChunkChainingIterator,
)
from redditwarp.iterators.chunking_iterator import ChunkingIterator

class TestCallChunkChainingIterator:
    def test_call_chunks_attrib(self) -> None:
        it = [lambda: [1]]
        ccci = CallChunkChainingIterator(it)
        assert ccci.call_chunks is it

    def test_simple_iteration(self) -> None:
        it = [
            lambda: [1],
            lambda: [2, 3],
            lambda: [4, 5, 6],
        ]
        ccci = CallChunkChainingIterator(it)
        assert list(ccci) == [1,2,3,4,5,6]

    def test_current_iter(self) -> None:
        l1 = [0, 1, 2]
        l2 = [3, 4]
        c1 = lambda: l1
        c2 = lambda: l2
        it = [c1, c2]
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
            def __call__(self) -> Iterable[int]:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                return [2]

        j = throw_on_first_call_then_return()
        it: Iterable[Callable[[], Iterable[int]]] = [
            lambda: [1],
            j,
            lambda: [3],
        ]
        ccci = CallChunkChainingIterator(it)
        assert ccci.current_callable is None
        assert next(ccci) == 1
        assert ccci.current_callable is None
        try:
            next(ccci)
        except RuntimeError:
            pass
        assert ccci.current_callable is j
        assert next(ccci) == 2
        assert ccci.current_callable is None
        assert next(ccci) == 3

    def test_current_callable_is_setable(self) -> None:
        it: Iterable[Callable[[], Iterable[int]]] = ()
        ccci = CallChunkChainingIterator(it)
        assert list(ccci) == []
        ccci.current_callable = lambda: (1,2,3)
        assert list(ccci) == [1,2,3]

class TestChunkSizeAdjustableCallChunkChainingIterator:
    def test_changing_chunk_size(self) -> None:
        it = list(range(10))
        ci = ChunkingIterator(it, 2)
        it2 = map(lambda x: lambda: x, ci)
        ccci = ChunkSizeAdjustableCallChunkChainingIterator(it2, ci)
        assert ccci.chunk_size == 2
        call_chunks = iter(ccci.call_chunks)
        assert tuple(next(call_chunks)()) == (0, 1)
        ccci.chunk_size = 5
        assert tuple(next(call_chunks)()) == (2,3,4,5,6)
