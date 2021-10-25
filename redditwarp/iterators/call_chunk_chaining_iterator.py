
from __future__ import annotations
from typing import Optional, Iterable, Iterator, Generic, Sequence

from .stubborn_caller_iterator import StubbornCallerIterator
from .unfaltering_chaining_iterator import UnfalteringChainingIterator
from .call_chunk_SYNC import CallChunk, TInput, TOutput

class CallChunkChainingIterator(Iterator[TOutput], Generic[TInput, TOutput]):
    """Evaluate call chunks and chain them together."""

    @property
    def current(self) -> Optional[CallChunk[Sequence[TInput], Sequence[TOutput]]]:
        c = self._call_iter.current
        if c is not None and not isinstance(c, CallChunk):
            raise RuntimeError('not a CallChunk')
        return c

    @current.setter
    def current(self, value: Optional[CallChunk[Sequence[TInput], Sequence[TOutput]]]) -> None:
        self._call_iter.current = value

    @property
    def current_iter(self) -> Iterator[TOutput]:
        return self._chain_itr.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[TOutput]) -> None:
        self._chain_itr.current_iter = value

    def __init__(self, chunks: Iterable[CallChunk[Sequence[TInput], Sequence[TOutput]]]) -> None:
        self.chunks: Iterable[CallChunk[Sequence[TInput], Sequence[TOutput]]] = chunks
        self._call_iter = StubbornCallerIterator(chunks)
        self._chain_itr = UnfalteringChainingIterator(self._call_iter)

    def __iter__(self) -> Iterator[TOutput]:
        return self

    def __next__(self) -> TOutput:
        return next(self._chain_itr)
