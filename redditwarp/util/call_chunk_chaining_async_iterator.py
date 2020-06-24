
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Callable, AsyncIterable, AsyncIterator, Awaitable

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator
from .unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator

T = TypeVar('T')

class CallChunkChainingAsyncIterator(Generic[T]):
    """Evaluate call chunks and chain them together."""

    @property
    def current_callable(self) -> Optional[Callable[[], Awaitable[AsyncIterable[T]]]]:
        return self._caller_iter.current

    @current_callable.setter
    def current_callable(self, value: Optional[Callable[[], Awaitable[AsyncIterable[T]]]]) -> None:
        self._caller_iter.current = value

    @property
    def current_iter(self) -> AsyncIterator[T]:
        return self._chain_iter.current_iter

    @current_iter.setter
    def current_iter(self, value: AsyncIterator[T]) -> None:
        self._chain_iter.current_iter = value

    def __init__(self, call_chunks: AsyncIterable[Callable[[], Awaitable[AsyncIterable[T]]]]) -> None:
        self.call_chunks = call_chunks
        self._caller_iter = StubbornCallerAsyncIterator(call_chunks)
        self._chain_iter = UnfalteringChainingAsyncIterator(self._caller_iter)

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        return await self._chain_iter.__anext__()
