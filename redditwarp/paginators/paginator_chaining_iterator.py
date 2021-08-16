
from __future__ import annotations
from typing import TypeVar, Iterator, Generic, Optional

from .paginator import Paginator

E = TypeVar('E')

class BasePaginatorChainingIterator(Iterator[E]):
    def __init__(self, paginator: Paginator[E], amount: Optional[int] = None) -> None:
        self._paginator: Paginator[E] = paginator
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

                if not self._paginator.next_available():
                    raise StopIteration

                if self._paginator.limit is not None and self.amount is not None:
                    remaining = self.amount - self.count
                    if remaining < self._paginator.limit:
                        self._paginator.limit = remaining

                it = self._paginator.fetch_next_result()
                self.current_iter = iter(it)

        raise StopIteration

__bound = 'Paginator[E]'
TPaginator = TypeVar('TPaginator', bound=Paginator)  # type: ignore[type-arg]

class PaginatorChainingIterator(BasePaginatorChainingIterator[E], Generic[TPaginator, E]):
    """Do not attempt to set the .paginator attribute. Doing so will not change the underlying pagination source."""

    def __init__(self, paginator: TPaginator, amount: Optional[int] = None) -> None:
        super().__init__(paginator, amount)
        self.paginator: TPaginator = paginator
