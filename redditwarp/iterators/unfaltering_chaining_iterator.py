
from __future__ import annotations
from typing import TypeVar, Iterable, Iterator

E = TypeVar('E')

class UnfalteringChainingIterator(Iterator[E]):
    """Like `itertools.chain.from_iterable()` but is able to continue when
    an exception occurs during iteration.

    Also has a `self.current_iter` attribute.
    """

    def __init__(self, source: Iterable[Iterable[E]]) -> None:
        self._iterator = iter(source)
        self.current_iter: Iterator[E] = iter(())

    def __iter__(self) -> Iterator[E]:
        return self

    def __next__(self) -> E:
        while True:
            for elem in self.current_iter:
                return elem
            self.current_iter = iter(next(self._iterator))
