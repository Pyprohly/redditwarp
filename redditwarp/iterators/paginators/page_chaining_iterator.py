
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Iterator, Generic, Optional
if TYPE_CHECKING:
    from .paginator import Paginator  # noqa: F401

from ..unfaltering_chaining_iterator import UnfalteringChainingIterator

E = TypeVar('E')
P = TypeVar('P', bound='Paginator')

class PageChainingIterator(Iterator[E], Generic[P, E]):
    @property
    def current_iter(self) -> Iterator[E]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[E]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, paginator: P, amount: Optional[int] = None) -> None:
        self.paginator = paginator
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
