
from __future__ import annotations
from typing import TypeVar, Sequence, Generic, Iterator, Optional

T = TypeVar('T')

class Paginator(Generic[T]):
    def __init__(self, *, limit: Optional[int] = None) -> None:
        self.limit: Optional[int] = limit

    def __iter__(self) -> Iterator[Sequence[T]]:
        while page := self.fetch():
            yield page

    def fetch(self) -> Sequence[T]:
        raise NotImplementedError

class OffsetPaginator(Paginator[T]):
    def __init__(self, *, limit: Optional[int] = None, offset: Optional[int] = None) -> None:
        super().__init__(limit=limit)
        self.offset: Optional[int] = offset

class CursorPaginator(Paginator[T]):
    def get_cursor(self) -> str:
        raise NotImplementedError

    def set_cursor(self, value: str) -> None:
        raise NotImplementedError


class MoreAvailablePaginator(Paginator[T]):
    def __iter__(self) -> Iterator[Sequence[T]]:
        if page := self.fetch():
            yield page
            while self.has_more_available() and (page := self.fetch()):
                yield page

    def has_more_available(self) -> bool:
        raise NotImplementedError

    def set_has_more_available_flag(self, value: bool) -> None:
        raise NotImplementedError


class Bidirectional:
    direction: bool

class Resettable:
    def reset(self) -> None:
        raise NotImplementedError
