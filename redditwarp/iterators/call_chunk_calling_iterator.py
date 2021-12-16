
from __future__ import annotations
from typing import Iterable, Iterator, Callable, TypeVar

from .stubborn_caller_iterator import StubbornCallerIterator

T = TypeVar('T')

class CallChunkCallingIterator(StubbornCallerIterator[T]):
    """Evaluate call chunks and return their results."""

    def __init__(self, chunks: Iterable[Callable[[], T]]) -> None:
        self.__chunk_iter: Iterator[Callable[[], T]] = iter(chunks)
        super().__init__(self.__chunk_iter)

    def get_chunk_iter(self) -> Iterator[Callable[[], T]]:
        return self.__chunk_iter
