
from __future__ import annotations
from typing import TypeVar, Generic, AsyncIterable, Callable, Optional, AsyncIterator, Awaitable

T = TypeVar('T')

class StubbornCallerAsyncIterator(Generic[T]):
    """Call each callable in the given iterator and return its result.

    If a call raises an exception it will propagate normally. Doing
    `next(self)` will re-attempt the call until it returns a value.
    """

    def __init__(self, iterable: AsyncIterable[Callable[[], Awaitable[T]]]) -> None:
        self._itr = iterable.__aiter__()
        self.current: Optional[Callable[[], Awaitable[T]]] = None

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        if self.current is None:
            self.current = await self._itr.__anext__()
        value = await self.current()
        self.current = None
        return value
