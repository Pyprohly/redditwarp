
import pytest

from redditwarp.util.chunked import chunked

def test_basics():
	assert tuple(chunked((1,2,3), 0)) == ()
	assert tuple(chunked((1,2,3), 1)) == ((1,), (2,), (3,))
	assert tuple(chunked((1,2,3), 2)) == ((1, 2), (3,))
	assert tuple(chunked((1,2,3), 3)) == ((1, 2, 3),)
	assert tuple(chunked((1,2,3), 4)) == ((1, 2, 3),)

def test_negative_size():
	with pytest.raises(ValueError):
		tuple(chunked((1, 2), -1))

def test_nonindexable_input():
	assert tuple(chunked(range(2), 2)) == ((0, 1),)
	assert tuple(chunked((i for i in (1,2,3)), 3)) == ((1, 2, 3),)
