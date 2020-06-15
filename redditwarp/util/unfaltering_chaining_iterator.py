
from __future__ import annotations
from typing import TypeVar, Iterable, Generic, Iterator

T = TypeVar('T')

class UnfalteringChainingIterator(Generic[T]):
    """Like `itertools.chain.from_iterable()` but is able to continue when
    an exception occurs during iteration.

    Also has a `self.current_iter` attribute.
    """

    def __init__(self, iterable: Iterable[Iterable[T]]) -> None:
        self._iterator = iter(iterable)
        self.current_iter: Iterator[T] = iter(())

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        while True:
            for element in self.current_iter:
                return element
            self.current_iter = iter(next(self._iterator))
