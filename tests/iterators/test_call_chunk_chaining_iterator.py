
from typing import Iterable, Sequence, Callable

from redditwarp.iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from redditwarp.iterators.call_chunk import CallChunk, TInput, TOutput

def new_call_chunk_of_sequences(
    operation: Callable[[Sequence[TInput]], Sequence[TOutput]],
    data: Sequence[TInput],
) -> CallChunk[Sequence[TInput], Sequence[TOutput]]:
    return CallChunk(operation, data)

class TestCallChunkChainingIterator:
    def test_get_chunking_iterator(self) -> None:
        it = [new_call_chunk_of_sequences(lambda x: x, [1])]
        ccci = CallChunkChainingIterator(it)
        assert list(ccci.get_chunking_iterator()) == it

    def test_simple_iteration(self) -> None:
        it = [
            new_call_chunk_of_sequences(lambda x: x, [1]),
            new_call_chunk_of_sequences(lambda x: x, [2, 3]),
            new_call_chunk_of_sequences(lambda x: x, [4, 5, 6]),
        ]
        ccci = CallChunkChainingIterator(it)
        assert list(ccci) == [1,2,3,4,5,6]

    def test_get_current_iterator(self) -> None:
        it = [
            new_call_chunk_of_sequences(lambda x: x, [0, 1, 2]),
            new_call_chunk_of_sequences(lambda x: x, [3, 4]),
        ]
        ccci = CallChunkChainingIterator(it)

        assert next(ccci) == 0
        assert list(ccci.current_iterator) == [1, 2]
        assert next(ccci) == 3
        assert next(ccci) == 4

        ccci.current_iterator = iter((8, 9))
        assert next(ccci) == 8
        assert next(ccci) == 9

    def test_exception_during_iteration(self) -> None:
        class ThrowOnFirstCallThenReturn:
            def __init__(self) -> None:
                self.call_count = 0
            def __call__(self, seq: Sequence[int]) -> Sequence[int]:
                self.call_count += 1
                if self.call_count == 1:
                    raise RuntimeError
                return seq

        j = new_call_chunk_of_sequences(ThrowOnFirstCallThenReturn(), [2])
        it = [
            new_call_chunk_of_sequences(lambda x: x, [1]),
            j,
            new_call_chunk_of_sequences(lambda x: x, [3]),
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
        assert ccci.current_callable is None

    def test_current_callable_is_setable(self) -> None:
        it: Iterable[CallChunk[Sequence[int], Sequence[int]]] = ()
        ccci = CallChunkChainingIterator(it)
        assert list(ccci) == []
        ccci.current_callable = new_call_chunk_of_sequences(lambda x: x, [1, 2, 3])
        assert list(ccci) == [1, 2, 3]
