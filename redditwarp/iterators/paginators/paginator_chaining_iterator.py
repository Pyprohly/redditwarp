
from __future__ import annotations
from typing import TypeVar, Iterator, Generic, Optional

from .paginator import Paginator

E = TypeVar('E')
__bound = 'Paginator[E]'
TPaginator = TypeVar('TPaginator', bound=Paginator)  # type: ignore[type-arg]

class PaginatorChainingIterator(Iterator[E], Generic[TPaginator, E]):
    def __init__(self, paginator: TPaginator, amount: Optional[int] = None) -> None:
        self.paginator = paginator
        self.amount = amount
        self.count = 0
        self.current_iter: Iterator[E] = iter(())

    def __iter__(self) -> Iterator[E]:
        return self

    def __next__(self) -> E:
        if self.amount is None or self.count < self.amount:
            while True:
                for elem in self.current_iter:
                    self.count += 1
                    return elem

                if self.paginator.limit is not None and self.amount is not None:
                    remaining = self.amount - self.count
                    if remaining < self.paginator.limit:
                        self.paginator.limit = remaining

                it = self.paginator.__next__()
                self.current_iter = iter(it)

        raise StopIteration
