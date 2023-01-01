
from __future__ import annotations
from typing import TypeVar, Iterator, Iterable, Callable, Optional

T = TypeVar('T')

class StubbornCallerIterator(Iterator[T]):
    """Call each callable in the given iterator and return its result.

    If a call raises an exception it will propagate normally. Doing
    `next(self)` will re-attempt the call until it returns a result.

    Has a `self.current` attribute to get the current callable.
    """

    def __init__(self, iterable: Iterable[Callable[[], T]]) -> None:
        self.__itr = iter(iterable)
        self.current: Optional[Callable[[], T]] = None

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self.current is None:
            self.current = next(self.__itr)
        ret = self.current()
        self.current = None
        return ret
