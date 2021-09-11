
from __future__ import annotations
from typing import TypeVar, Iterator, Generic, Optional

from .paginator import Paginator

E = TypeVar('E')

class BasePaginatorChainingIterator(Iterator[E]):
    def __init__(self, paginator: Paginator[E], amount: Optional[int] = None) -> None:
        self._pgr: Paginator[E] = paginator
        self.remaining = amount
        self.current_iter: Iterator[E] = iter(())

    def __iter__(self) -> Iterator[E]:
        return self

    def __next__(self) -> E:
        if self.remaining is None or self.remaining > 0:
            while True:
                for elem in self.current_iter:
                    if self.remaining is not None:
                        self.remaining -= 1
                    return elem

                if not self._pgr.next_available():
                    raise StopIteration

                if self._pgr.limit is not None and self.remaining is not None:
                    if self.remaining < self._pgr.limit:
                        self._pgr.limit = self.remaining

                it = self._pgr.next_result()
                self.current_iter = iter(it)

        raise StopIteration

__bound = 'Paginator[E]'
TPaginator = TypeVar('TPaginator', bound=Paginator)  # type: ignore[type-arg]

class PaginatorChainingIterator(BasePaginatorChainingIterator[E], Generic[TPaginator, E]):
    """Do not attempt to set the .paginator attribute. Doing so will not change the underlying pagination source."""

    def __init__(self, paginator: TPaginator, amount: Optional[int] = None) -> None:
        super().__init__(paginator, amount)
        self.paginator: TPaginator = paginator
