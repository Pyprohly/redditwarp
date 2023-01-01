
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Optional
if TYPE_CHECKING:
    from typing import Iterable, Iterator, Callable, Awaitable, AsyncIterator

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator

T = TypeVar('T')

class CallChunkCallingAsyncIterator(Generic[T]):
    """Evaluate call chunks and return their results."""

    @property
    def current_callable(self) -> Optional[Callable[[], Awaitable[T]]]:
        return self.__calling_itr.current

    @current_callable.setter
    def current_callable(self, value: Optional[Callable[[], Awaitable[T]]]) -> None:
        self.__calling_itr.current = value

    def __init__(self, chunks: Iterable[Callable[[], Awaitable[T]]]) -> None:
        self.__chunking_itr: Iterator[Callable[[], Awaitable[T]]] = iter(chunks)
        self.__calling_itr: StubbornCallerAsyncIterator[T] = StubbornCallerAsyncIterator(self.__chunking_itr)

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        return await self.__calling_itr.__anext__()

    def get_chunking_iterator(self) -> Iterator[Callable[[], Awaitable[T]]]:
        return self.__chunking_itr
