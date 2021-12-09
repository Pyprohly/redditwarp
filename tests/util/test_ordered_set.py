
from __future__ import annotations

import pytest

from redditwarp.util.ordered_set import OrderedSet, BoundedSet


class TestOrderedSet:
    def test_basics(self) -> None:
        ds = OrderedSet(range(3))
        assert list(ds) == [0,1,2]
        ds.add(5)
        assert list(ds) == [0,1,2,5]

    def test_constructor_consumes_iterator(self) -> None:
        it = iter(range(5))
        OrderedSet(it)
        assert list(it) == []

    def test_add(self) -> None:
        ds: OrderedSet[int] = OrderedSet(())
        ds.add(1)
        ds.add(2)
        ds.add(2)
        assert len(ds) == 2
        assert list(ds) == [1, 2]
        ds.add(3)
        ds.add(4)
        assert list(ds) == [1, 2, 3, 4]

    def test_discard(self) -> None:
        ds = OrderedSet(range(3))
        ds.discard(1)
        assert set(ds) == {0, 2}
        ds.discard(1)
        assert set(ds) == {0, 2}

    def test_set_operations(self) -> None:
        p = OrderedSet((1,2,4)) | OrderedSet((2,3,4))
        assert p == {1,2,4,3}
        assert list(p) == [1,2,4,3]
        p = OrderedSet((1,2,4)) & OrderedSet((2,3,4))
        assert p == {2,4}
        assert list(p) == [2,4]


class TestBoundedSet:
    def test_constructor_basics(self) -> None:
        bs = BoundedSet(range(5), 3)
        assert list(bs) == [2, 3, 4]
        bs.add(7)
        assert list(bs) == [3, 4, 7]
        assert bs.capacity == 3

        bs = BoundedSet(range(5), 0)
        assert set(bs) == set()
        bs.add(8)
        assert set(bs) == set()
        assert bs.capacity == 0

        with pytest.raises(ValueError):
            BoundedSet(range(5), -1)

    def test_constructor_consumes_iterator(self) -> None:
        it = iter(range(5))
        BoundedSet(it, 3)
        assert list(it) == []

        it = iter(range(5))
        BoundedSet(it, 0)
        assert list(it) == []

    def test_add(self) -> None:
        bs: BoundedSet[int] = BoundedSet((), 3)
        bs.add(1)
        bs.add(2)
        bs.add(2)
        assert len(bs) == 2
        assert list(bs) == [1, 2]
        bs.add(3)
        bs.add(4)
        assert list(bs) == [2, 3, 4]

    def test_discard(self) -> None:
        bs = BoundedSet(range(3), 3)
        bs.discard(1)
        assert set(bs) == {0, 2}
        bs.discard(1)
        assert set(bs) == {0, 2}

    def test_set_operations(self) -> None:
        p = BoundedSet((1,2,4), 8) | BoundedSet((2,3,4), 9)
        assert p == {1,2,4,3}
        assert list(p) == [1,2,4,3]
        assert isinstance(p, BoundedSet)
        assert p.capacity == 8
        p = BoundedSet((1,2,4), 8) & BoundedSet((2,3,4), 9)
        assert p == {2,4}
        assert list(p) == [2,4]
        assert isinstance(p, BoundedSet)
        assert p.capacity == 8

        q = BoundedSet('abc', 3) | BoundedSet('123', 1)
        assert list(q) == ['b', 'c', '3']
        q = BoundedSet('abc', 3) | BoundedSet('123', 2)
        assert list(q) == ['c', '2', '3']
