
from __future__ import annotations
from typing import TypeVar, Iterable, Iterator

E = TypeVar('E')

class UnfalteringChainingIterator(Iterator[E]):
    """Like `itertools.chain.from_iterable()` but is able to continue when
    an exception occurs during iteration.

    Also has a `self.current_iterator` attribute to get the current iterator.
    """

    def __init__(self, source: Iterable[Iterable[E]]) -> None:
        self.__iterator = iter(source)
        self.current_iterator: Iterator[E] = iter(())
        ("")

    def __iter__(self) -> Iterator[E]:
        return self

    def __next__(self) -> E:
        while True:
            for elem in self.current_iterator:
                return elem
            self.current_iterator = iter(next(self.__iterator))
