
import pytest

from redditwarp.iterators.chunking import chunked, ChunkingIterator

class TestChunked:
    def test_basics(self) -> None:
        assert tuple(chunked((1,2,3), 0)) == ()
        assert tuple(chunked((1,2,3), 1)) == ((1,), (2,), (3,))
        assert tuple(chunked((1,2,3), 2)) == ((1, 2), (3,))
        assert tuple(chunked((1,2,3), 3)) == ((1, 2, 3),)
        assert tuple(chunked((1,2,3), 4)) == ((1, 2, 3),)

    def test_nonindexable_input(self) -> None:
        assert tuple(chunked(range(2), 2)) == ((0, 1),)
        assert tuple(chunked((i for i in (1,2,3)), 3)) == ((1, 2, 3),)

    def test_negative_size(self) -> None:
        with pytest.raises(ValueError):
            tuple(chunked((1, 2), -1))

class TestChunkingIterator:
    def test_basics(self) -> None:
        assert tuple(ChunkingIterator((1,2,3), 0)) == ()
        assert tuple(ChunkingIterator((1,2,3), 1)) == ((1,), (2,), (3,))
        assert tuple(ChunkingIterator((1,2,3), 2)) == ((1, 2), (3,))
        assert tuple(ChunkingIterator((1,2,3), 3)) == ((1, 2, 3),)
        assert tuple(ChunkingIterator((1,2,3), 4)) == ((1, 2, 3),)

    def test_nonindexable_input(self) -> None:
        assert tuple(ChunkingIterator(range(2), 2)) == ((0, 1),)
        assert tuple(ChunkingIterator((i for i in (1,2,3)), 3)) == ((1, 2, 3),)

    def test_changing_size(self) -> None:
        it = tuple(range(10))
        ci = ChunkingIterator(it, 0)
        assert tuple(ci) == ()
        ci.size = 1
        assert tuple(next(ci)) == (0,)
        ci.size = 2
        assert tuple(next(ci)) == (1, 2)
        ci.size = 3
        assert tuple(next(ci)) == (3, 4, 5)
        ci.size = 1
        assert tuple(next(ci)) == (6,)
        ci.size = 5
        assert tuple(next(ci)) == (7, 8, 9)
