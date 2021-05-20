
from typing import Sequence
from redditwarp.iterators.paginators.bidirectional_async_paginator import BidirectionalAsyncPaginator

class MyBidirectionalAsyncPaginator(BidirectionalAsyncPaginator[int]):
    async def next_result(self) -> Sequence[int]:
        return []

    def has_next(self) -> bool:
        return True

def test_direction() -> None:
    p = MyBidirectionalAsyncPaginator()
    assert p.get_direction()

    p.set_direction(True)
    assert p.get_direction()
    p.set_direction(True)
    assert p.get_direction()

    p.set_direction(False)
    assert not p.get_direction()
    p.set_direction(False)
    assert not p.get_direction()

    p.set_direction(True)
    p.change_direction()
    assert not p.get_direction()
    p.change_direction()
    assert p.get_direction()
