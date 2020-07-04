
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Optional, Callable, Iterable, Iterator, Any
if TYPE_CHECKING:
    from .chunking_iterator import ChunkingIterator

from .stubborn_caller_iterator import StubbornCallerIterator
from .unfaltering_chaining_iterator import UnfalteringChainingIterator

T = TypeVar('T')

class CallChunkChainingIterator(Generic[T]):
    """Evaluate call chunks and chain them together."""

    @property
    def current_callable(self) -> Optional[Callable[[], Iterable[T]]]:
        return self._caller_iter.current

    @current_callable.setter
    def current_callable(self, value: Optional[Callable[[], Iterable[T]]]) -> None:
        self._caller_iter.current = value

    @property
    def current_iter(self) -> Iterator[T]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[T]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, call_chunks: Iterable[Callable[[], Iterable[T]]]) -> None:
        self.call_chunks = call_chunks
        self._caller_iter = StubbornCallerIterator(call_chunks)
        self._chain_iter = UnfalteringChainingIterator(self._caller_iter)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self._chain_iter)

class ChunkSizeAdjustableCallChunkChainingIterator(CallChunkChainingIterator[T]):
    @property
    def chunk_size(self) -> int:
        return self._chunk_iter.size

    @chunk_size.setter
    def chunk_size(self, value: int) -> None:
        self._chunk_iter.size = value

    def __init__(self,
        call_chunks: Iterable[Callable[[], Iterable[T]]],
        chunk_iter: ChunkingIterator[Any],
    ) -> None:
        super().__init__(call_chunks)
        self._chunk_iter = chunk_iter
