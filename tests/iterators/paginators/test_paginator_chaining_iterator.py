
from typing import List, Iterable

from redditwarp.iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from redditwarp.iterators.paginators.paginator import Paginator

class IntIterableToPaginator(Paginator[int]):
    def __init__(self, it: Iterable[List[int]]) -> None:
        super().__init__()
        self._proceed = True
        self._itr = iter(it)

    def next_result(self) -> List[int]:
        try:
            return next(self._itr)
        except StopIteration:
            self._proceed = False
            raise

    def has_next(self) -> bool:
        return self._proceed


def test_simple_iteration() -> None:
    p = IntIterableToPaginator([
        [1],
        [2, 3],
        [4, 5, 6],
    ])
    pci: PaginatorChainingIterator[IntIterableToPaginator, int] = PaginatorChainingIterator(p)
    assert list(pci) == [1,2,3,4,5,6]

def test_current_iter() -> None:
    p = IntIterableToPaginator([
        [0, 1, 2],
        [3, 4],
    ])
    pci: PaginatorChainingIterator[IntIterableToPaginator, int] = PaginatorChainingIterator(p)

    assert next(pci) == 0
    assert list(pci.current_iter) == [1, 2]
    assert next(pci) == 3
    assert next(pci) == 4

    pci.current_iter = iter((8, 9))
    assert next(pci) == 8
    assert next(pci) == 9

def test_amount() -> None:
    p = IntIterableToPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci: PaginatorChainingIterator[IntIterableToPaginator, int] = PaginatorChainingIterator(p, 6)
    assert pci.amount == 6
    assert pci.count == 0
    assert next(pci) == 10
    assert pci.count == 1
    assert list(pci) == [20,30,40,50,60]
    assert pci.count == 6

    p = IntIterableToPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci = PaginatorChainingIterator(p)
    assert pci.amount is None
    assert list(pci) == [10,20,30,40,50,60,70,80]
    assert pci.count == 8

def test_efficient_pagination_limit() -> None:
    p = IntIterableToPaginator([
        list(range(100)),
        list(range(23)),
    ])
    p.limit = 100
    pci: PaginatorChainingIterator[IntIterableToPaginator, int] = PaginatorChainingIterator(p, 123)
    for _ in range(100):
        next(pci)
    assert pci.count == 100
    assert p.limit == 100
    next(pci)
    assert p.limit == 23
