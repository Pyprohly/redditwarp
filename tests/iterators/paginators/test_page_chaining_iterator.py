
from typing import List

from redditwarp.iterators.paginators.page_chaining_iterator import PageChainingIterator
from redditwarp.iterators.paginators.paginator import Paginator


def test_simple_iteration() -> None:
    class MyPaginator(Paginator[int]):
        def __init__(self) -> None:
            super().__init__()
            self._itr = iter([
                [1],
                [2, 3],
                [4, 5, 6],
            ])

        def __next__(self) -> List[int]:
            return next(self._itr)

    p = MyPaginator()
    pci = PageChainingIterator(p)
    assert list(pci) == [1,2,3,4,5,6]

def test_current_iter() -> None:
    class MyPaginator(Paginator[int]):
        def __init__(self) -> None:
            super().__init__()
            self._itr = iter([
                [0, 1, 2],
                [3, 4],
            ])

        def __next__(self) -> List[int]:
            return next(self._itr)

    pci = PageChainingIterator(MyPaginator())

    assert next(pci) == 0
    assert list(pci.current_iter) == [1, 2]
    assert next(pci) == 3
    assert next(pci) == 4

    pci.current_iter = iter((8, 9))
    assert next(pci) == 8
    assert next(pci) == 9

def test_amount() -> None:
    class MyPaginator(Paginator[int]):
        def __init__(self) -> None:
            super().__init__()
            self._itr = iter([
                [10, 20, 30, 40],
                [50, 60, 70, 80],
            ])

        def __next__(self) -> List[int]:
            return next(self._itr)

    pci = PageChainingIterator(MyPaginator(), 6)
    assert pci.amount == 6
    assert pci.count == 0
    assert next(pci) == 10
    assert pci.count == 1
    assert list(pci) == [20,30,40,50,60]
    assert pci.count == 6

    pci = PageChainingIterator(MyPaginator())
    assert pci.amount is None
    assert list(pci) == [10,20,30,40,50,60,70,80]
    assert pci.count == 8
