
from __future__ import annotations
from typing import TypeVar, AsyncIterator, Callable, Optional, Awaitable, Iterable

T = TypeVar('T')

class StubbornCallerAsyncIterator(AsyncIterator[T]):
    def __init__(self, iterable: Iterable[Callable[[], Awaitable[T]]]) -> None:
        self.__itr = iter(iterable)
        self.current: Optional[Callable[[], Awaitable[T]]] = None

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        if self.current is None:
            try:
                self.current = next(self.__itr)
            except StopIteration:
                raise StopAsyncIteration
        ret = await self.current()
        self.current = None
        return ret
