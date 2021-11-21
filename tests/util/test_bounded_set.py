
from __future__ import annotations

import pytest

from redditwarp.util.bounded_set import BoundedSet

def test_constructor_basics() -> None:
    bs = BoundedSet(range(5), 3)
    assert set(bs) == {2, 3, 4}
    bs.add(7)
    assert set(bs) == {3, 4, 7}

    bs = BoundedSet(range(5), 0)
    assert set(bs) == set()
    bs.add(8)
    assert set(bs) == set()

    with pytest.raises(ValueError):
        BoundedSet(range(5), -1)

def test_constructor_consumes_iterable() -> None:
    it = iter(range(5))
    BoundedSet(it, 3)
    assert list(it) == []

    it = iter(range(5))
    BoundedSet(it, 0)
    assert list(it) == []

def test_add() -> None:
    bs: BoundedSet[int] = BoundedSet((), 3)
    bs.add(1)
    bs.add(2)
    bs.add(2)
    assert len(bs) == 2
    assert set(bs) == {1, 2}
    bs.add(3)
    bs.add(4)
    assert set(bs) == {2, 3, 4}

def test_discard() -> None:
    bs = BoundedSet(range(5), 3)
    bs.discard(3)
    assert set(bs) == {2, 4}
    bs.discard(404)
    assert set(bs) == {2, 4}

def test_add_duplicates_and_test_ordering() -> None:
    bs: BoundedSet[int] = BoundedSet([], 3)
    bs.add(0)
    bs.add(0)
    assert set(bs) == {0}
    assert list(bs.ordering()) == [0]
