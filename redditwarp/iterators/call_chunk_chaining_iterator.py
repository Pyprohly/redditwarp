
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Optional
if TYPE_CHECKING:
    from typing import Iterable, Iterator, Callable, Sequence

from .stubborn_caller_iterator import StubbornCallerIterator
from .unfaltering_chaining_iterator import UnfalteringChainingIterator

T = TypeVar('T')

class CallChunkChainingIterator(Generic[T]):
    """Evaluate call chunks and chain them together."""

    @property
    def current_callable(self) -> Optional[Callable[[], Sequence[T]]]:
        return self.__calling_itr.current

    @current_callable.setter
    def current_callable(self, value: Optional[Callable[[], Sequence[T]]]) -> None:
        self.__calling_itr.current = value

    @property
    def current_iterator(self) -> Iterator[T]:
        return self.__chaining_itr.current_iterator

    @current_iterator.setter
    def current_iterator(self, value: Iterator[T]) -> None:
        self.__chaining_itr.current_iterator = value

    def __init__(self, chunks: Iterable[Callable[[], Sequence[T]]]) -> None:
        self.__chunking_itr: Iterator[Callable[[], Sequence[T]]] = iter(chunks)
        self.__calling_itr: StubbornCallerIterator[Sequence[T]] = StubbornCallerIterator(self.__chunking_itr)
        self.__chaining_itr: UnfalteringChainingIterator[T] = UnfalteringChainingIterator(self.__calling_itr)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self.__chaining_itr)

    def get_chunking_iterator(self) -> Iterator[Callable[[], Sequence[T]]]:
        return self.__chunking_itr
