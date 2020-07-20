
from __future__ import annotations
from typing import TypeVar, Iterable, Iterator

T = TypeVar('T')

class UnfalteringChainingIterator(Iterator[T]):
    """Like `itertools.chain.from_iterable()` but is able to continue when
    an exception occurs during iteration.

    Also has a `self.current_iter` attribute.
    """

    def __init__(self, source: Iterable[Iterable[T]]) -> None:
        self._iterator = iter(source)
        self.current_iter: Iterator[T] = iter(())

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        while True:
            for link in self.current_iter:
                return link
            self.current_iter = iter(next(self._iterator))
