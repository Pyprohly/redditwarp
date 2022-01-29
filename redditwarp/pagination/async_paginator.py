
from __future__ import annotations
from typing import TypeVar, Sequence, Generic, AsyncIterator, Optional

T = TypeVar('T')

class AsyncPaginator(Generic[T]):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        self.limit: Optional[int] = limit

    async def __aiter__(self) -> AsyncIterator[Sequence[T]]:
        while x := await self.fetch():
            yield x

    async def fetch(self) -> Sequence[T]:
        raise NotImplementedError

class OffsetAsyncPaginator(AsyncPaginator[T]):
    def __init__(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> None:
        super().__init__(limit=limit)
        self.offset: Optional[int] = offset

class CursorAsyncPaginator(AsyncPaginator[T]):
    def get_cursor(self) -> str:
        raise NotImplementedError

    def set_cursor(self, value: str) -> None:
        raise NotImplementedError


class MoreAvailableAsyncPaginator(AsyncPaginator[T]):
    async def __aiter__(self) -> AsyncIterator[Sequence[T]]:
        if x := await self.fetch():
            yield x
        while self.more_available() and (x := await self.fetch()):
            yield x

    def more_available(self) -> bool:
        raise NotImplementedError

    def set_more_available_flag(self, value: bool) -> None:
        raise NotImplementedError


class Bidirectional:
    direction: bool

class Resettable:
    def reset(self) -> None:
        raise NotImplementedError
