
from __future__ import annotations
from typing import TypeVar, Iterator, Generic, Optional, Sequence

from .paginator import Paginator

E = TypeVar('E')

class PaginatorChainingIterator(Iterator[E]):
    def __init__(self, paginator: Paginator[E], amount: Optional[int] = None) -> None:
        self._paginator: Paginator[E] = paginator
        self._paginator_iterator: Iterator[Sequence[E]] = iter(paginator)
        self.remaining: Optional[int] = amount
        ("")
        self.current_iterator: Iterator[E] = iter(())
        ("")

    def __iter__(self) -> Iterator[E]:
        return self

    def __next__(self) -> E:
        limit = self._paginator.limit
        remaining = self.remaining
        if remaining is None or remaining > 0:
            while True:
                for elem in self.current_iterator:
                    if self.remaining is not None:
                        self.remaining -= 1
                    return elem

                if (limit is not None and remaining is not None) and limit > remaining:
                    self._paginator.limit = remaining

                it = next(self._paginator_iterator)
                self.current_iterator = iter(it)

        raise StopIteration



__bound = 'Paginator[E]'
TPaginator = TypeVar('TPaginator', bound=Paginator)  # type: ignore[type-arg]

class ImpartedPaginatorChainingIterator(PaginatorChainingIterator[E], Generic[TPaginator, E]):
    def __init__(self, paginator: TPaginator, amount: Optional[int] = None) -> None:
        super().__init__(paginator, amount)
        self.__paginator: TPaginator = paginator

    def get_paginator(self) -> TPaginator:
        return self.__paginator
