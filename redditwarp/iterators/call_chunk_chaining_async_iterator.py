
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Callable, Iterable, AsyncIterator, Iterator, Awaitable, Any
if TYPE_CHECKING:
    from .chunking_iterator import ChunkingIterator

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator
from .unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator

T = TypeVar('T')

class CallChunkChainingAsyncIterator(AsyncIterator[T]):
    """Evaluate call chunks and chain them together."""

    @property
    def current_callable(self) -> Optional[Callable[[], Awaitable[Iterable[T]]]]:
        return self._caller_iter.current

    @current_callable.setter
    def current_callable(self, value: Optional[Callable[[], Awaitable[Iterable[T]]]]) -> None:
        self._caller_iter.current = value

    @property
    def current_iter(self) -> Iterator[T]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[T]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, call_chunks: Iterable[Callable[[], Awaitable[Iterable[T]]]]) -> None:
        self.call_chunks = call_chunks
        self._caller_iter = StubbornCallerAsyncIterator(call_chunks)
        self._chain_iter = UnfalteringChainingAsyncIterator(self._caller_iter)

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        return await self._chain_iter.__anext__()

class ChunkSizeAdjustableCallChunkChainingAsyncIterator(CallChunkChainingAsyncIterator[T]):
    """An extension to CallChunkChainingAsyncIterator that lets you control the call chunk size."""

    @property
    def chunk_size(self) -> int:
        return self._chunk_iter.size

    @chunk_size.setter
    def chunk_size(self, value: int) -> None:
        self._chunk_iter.size = value

    def __init__(self,
        call_chunks: Iterable[Callable[[], Awaitable[Iterable[T]]]],
        chunk_iter: ChunkingIterator[Any],
    ) -> None:
        super().__init__(call_chunks)
        self._chunk_iter = chunk_iter
