
from __future__ import annotations
from typing import Optional, Iterable, Iterator, Generic

from .stubborn_caller_iterator import StubbornCallerIterator
from .call_chunk_SYNC import CallChunk, TInput, TOutput

class CallChunkCallingIterator(Iterator[TOutput], Generic[TInput, TOutput]):
    """Evaluate call chunks and return their results."""

    @property
    def current(self) -> Optional[CallChunk[TInput, TOutput]]:
        c = self._call_iter.current
        if c is not None and not isinstance(c, CallChunk):
            raise RuntimeError('not a CallChunk')
        return c

    @current.setter
    def current(self, value: Optional[CallChunk[TInput, TOutput]]) -> None:
        self._call_iter.current = value

    def __init__(self, chunks: Iterable[CallChunk[TInput, TOutput]]) -> None:
        self.chunks = chunks
        self._call_iter = StubbornCallerIterator(chunks)

    def __iter__(self) -> Iterator[TOutput]:
        return self

    def __next__(self) -> TOutput:
        return next(self._call_iter)
