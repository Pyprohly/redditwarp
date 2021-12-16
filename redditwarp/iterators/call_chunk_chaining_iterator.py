
from __future__ import annotations
from typing import Iterable, Iterator, Sequence, TypeVar, Callable

from .stubborn_caller_iterator import StubbornCallerIterator
from .unfaltering_chaining_iterator import UnfalteringChainingIterator

T = TypeVar('T')

class CallChunkChainingIterator(UnfalteringChainingIterator[T]):
    """Evaluate call chunks and chain them together."""

    def __init__(self, chunks: Iterable[Callable[[], Sequence[T]]]) -> None:
        self.__chunk_iter: Iterator[Callable[[], Sequence[T]]] = iter(chunks)
        self.__caller_iter: Iterator[Sequence[T]] = StubbornCallerIterator(self.__chunk_iter)
        super().__init__(self.__caller_iter)

    def get_chunk_iter(self) -> Iterator[Callable[[], Sequence[T]]]:
        return self.__chunk_iter

    def get_caller_iter(self) -> Iterator[Sequence[T]]:
        return self.__caller_iter
