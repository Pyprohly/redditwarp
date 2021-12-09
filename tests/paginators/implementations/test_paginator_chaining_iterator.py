
from typing import Sequence

from redditwarp.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from redditwarp.paginators.paginator import Paginator

class MyPaginator(Paginator[int]):
    def __init__(self, seq: Sequence[Sequence[int]]) -> None:
        super().__init__()
        self.seq = seq
        self.index = -1
        self.proceed = True

    def next_available(self) -> bool:
        return self.proceed

    def fetch_next(self) -> Sequence[int]:
        self.index += 1
        if self.index >= len(self.seq) - 1:
            self.proceed = False
        return self.seq[self.index]


def test_simple_iteration() -> None:
    p = MyPaginator([
        [1],
        [2, 3],
        [4, 5, 6],
    ])
    pci: PaginatorChainingIterator[int] = PaginatorChainingIterator(p)
    assert list(pci) == [1,2,3,4,5,6]

def test_current_iter() -> None:
    p = MyPaginator([
        [0, 1, 2],
        [3, 4],
    ])
    pci: PaginatorChainingIterator[int] = PaginatorChainingIterator(p)

    assert next(pci) == 0
    assert list(pci.current_iter) == [1, 2]
    assert next(pci) == 3
    assert next(pci) == 4

    pci.current_iter = iter((8, 9))
    assert next(pci) == 8
    assert next(pci) == 9

def test_amount() -> None:
    p = MyPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci: PaginatorChainingIterator[int] = PaginatorChainingIterator(p, 6)
    assert pci.remaining == 6
    assert next(pci) == 10
    assert pci.remaining == 5
    assert list(pci) == [20,30,40,50,60]
    assert pci.remaining == 0

    p = MyPaginator([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
    ])
    pci = PaginatorChainingIterator(p)
    assert pci.remaining is None
    assert list(pci) == [10,20,30,40,50,60,70,80]
    assert pci.remaining is None

def test_efficient_pagination_limit() -> None:
    p = MyPaginator([
        list(range(100)),
        list(range(23)),
    ])
    p.limit = 100
    pci: PaginatorChainingIterator[int] = PaginatorChainingIterator(p, 123)
    for _ in range(100):
        next(pci)
    assert pci.remaining == 23
    assert p.limit == 100
    next(pci)
    assert p.limit == 23
