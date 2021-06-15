
from __future__ import annotations
from typing import Optional, Iterable, AsyncIterator, Iterator, Generic

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator
from .unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator
from .call_chunk_ASYNC import CallChunk, TInput, TOutput

class CallChunkChainingAsyncIterator(AsyncIterator[TOutput], Generic[TInput, TOutput]):
    @property
    def current(self) -> Optional[CallChunk[TInput, TOutput]]:
        c = self._call_iter.current
        if c is not None and not isinstance(c, CallChunk):
            raise RuntimeError('type is not CallChunk')
        return c

    @current.setter
    def current(self, value: Optional[CallChunk[TInput, TOutput]]) -> None:
        self._call_iter.current = value

    @property
    def current_iter(self) -> Iterator[TOutput]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: Iterator[TOutput]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, chunks: Iterable[CallChunk[TInput, TOutput]]) -> None:
        self.chunks = chunks
        self._call_iter = StubbornCallerAsyncIterator(chunks)
        self._chain_iter = UnfalteringChainingAsyncIterator(self._call_iter)

    def __aiter__(self) -> AsyncIterator[TOutput]:
        return self

    async def __anext__(self) -> TOutput:
        return await self._chain_iter.__anext__()
