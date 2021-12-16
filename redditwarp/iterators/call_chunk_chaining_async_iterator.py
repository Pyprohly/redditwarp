
from __future__ import annotations
from typing import Iterable, Iterator, AsyncIterator, Sequence, Awaitable, TypeVar, Callable

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator
from .unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator

T = TypeVar('T')

class CallChunkChainingAsyncIterator(UnfalteringChainingAsyncIterator[T]):
    """Evaluate call chunks and chain them together."""

    def __init__(self, chunks: Iterable[Callable[[], Awaitable[Sequence[T]]]]) -> None:
        self.__chunk_iter: Iterator[Callable[[], Awaitable[Sequence[T]]]] = iter(chunks)
        self.__caller_iter: AsyncIterator[Sequence[T]] = StubbornCallerAsyncIterator(self.__chunk_iter)
        super().__init__(self.__caller_iter)

    def get_chunk_iter(self) -> Iterator[Callable[[], Awaitable[Sequence[T]]]]:
        return self.__chunk_iter

    def get_caller_iter(self) -> AsyncIterator[Sequence[T]]:
        return self.__caller_iter
