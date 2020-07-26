
from __future__ import annotations
from typing import TypeVar, Iterator, Generic, Optional

from .paginator import Paginator
from ..unfaltering_chaining_iterator import UnfalteringChainingIterator

E = TypeVar('E')

class PageChainingIterator(Iterator[E]):
    @property
    def current_iter(self) -> Iterator[E]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[E]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, paginator: Paginator[E], amount: Optional[int] = None) -> None:
        self.amount = amount
        self.count = 0
        self._chain_iter: UnfalteringChainingIterator[E] = UnfalteringChainingIterator(paginator)

    def __iter__(self) -> Iterator[E]:
        return self

    def __next__(self) -> E:
        if self.amount is None or self.count < self.amount:
            el = next(self._chain_iter)
            self.count += 1
            return el
        raise StopIteration

Paginator_E = Paginator[E]
P = TypeVar('P', bound=Paginator_E)

class PaginatorKeepingPageChainingIterator(PageChainingIterator[E], Generic[P, E]):
    def __init__(self, paginator: P, amount: Optional[int]) -> None:
        super().__init__(paginator, amount)
        self.paginator = paginator
