
from __future__ import annotations
from typing import Optional, Iterable, AsyncIterator, Generic

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator
from .call_chunk_ASYNC import CallChunk, TInput, TOutput

class CallChunkCallingAsyncIterator(AsyncIterator[TOutput], Generic[TInput, TOutput]):
    """Evaluate call chunks and chain them together."""

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
        self.chunks: Iterable[CallChunk[TInput, TOutput]] = chunks
        self._call_iter = StubbornCallerAsyncIterator(chunks)

    def __aiter__(self) -> AsyncIterator[TOutput]:
        return self

    async def __anext__(self) -> TOutput:
        return await self._call_iter.__anext__()
