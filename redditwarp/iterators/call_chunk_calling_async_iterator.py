
from __future__ import annotations
from typing import Iterable, Iterator, Callable, TypeVar, Awaitable

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator

T = TypeVar('T')

class CallChunkCallingAsyncIterator(StubbornCallerAsyncIterator[T]):
    """Evaluate call chunks and return their results."""

    def __init__(self, chunks: Iterable[Callable[[], Awaitable[T]]]) -> None:
        self.__chunk_iter: Iterator[Callable[[], Awaitable[T]]] = iter(chunks)
        super().__init__(self.__chunk_iter)

    def get_chunk_iter(self) -> Iterator[Callable[[], Awaitable[T]]]:
        return self.__chunk_iter
