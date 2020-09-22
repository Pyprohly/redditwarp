
from typing import Sequence
from redditwarp.iterators.paginators.bidirectional_paginator import BidirectionalPaginator

class MyBidirectionalPaginator(BidirectionalPaginator[int]):
    def __next__(self) -> Sequence[int]:
        return []

def test_direction() -> None:
    p = MyBidirectionalPaginator()
    assert p.get_direction()
    assert p.has_next and not p.has_prev
    p.set_direction(True)
    assert p.get_direction()
    assert p.has_next and not p.has_prev
    p.set_direction(True)
    assert p.get_direction()
    assert p.has_next and not p.has_prev

    p.set_direction(False)
    assert not p.get_direction()
    assert not p.has_next and p.has_prev
    p.set_direction(False)
    assert not p.get_direction()
    assert not p.has_next and p.has_prev

    p.change_direction()
    assert p.get_direction()
    assert p.has_next and not p.has_prev
    p.change_direction()
    assert not p.get_direction()
    assert not p.has_next and p.has_prev
