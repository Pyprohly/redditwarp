
from typing import Sequence
from redditwarp.iterators.paginators.bidirectional_async_paginator import BidirectionalAsyncPaginator

class MyBidirectionalAsyncPaginator(BidirectionalAsyncPaginator[int]):
    async def __anext__(self) -> Sequence[int]:
        return []

def test_direction() -> None:
    p = MyBidirectionalAsyncPaginator()
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
