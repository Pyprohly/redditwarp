
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Optional
if TYPE_CHECKING:
    from typing import Iterable, Iterator, Callable

from .stubborn_caller_iterator import StubbornCallerIterator

T = TypeVar('T')

class CallChunkCallingIterator(Generic[T]):
    """Evaluate call chunks and return their results."""

    @property
    def current_callable(self) -> Optional[Callable[[], T]]:
        return self.__calling_itr.current

    @current_callable.setter
    def current_callable(self, value: Optional[Callable[[], T]]) -> None:
        self.__calling_itr.current = value

    def __init__(self, chunks: Iterable[Callable[[], T]]) -> None:
        self.__chunking_itr: Iterator[Callable[[], T]] = iter(chunks)
        self.__calling_itr: StubbornCallerIterator[T] = StubbornCallerIterator(self.__chunking_itr)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self.__calling_itr)

    def get_chunking_iterator(self) -> Iterator[Callable[[], T]]:
        return self.__chunking_itr
