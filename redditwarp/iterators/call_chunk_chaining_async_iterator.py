
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Optional
if TYPE_CHECKING:
    from typing import Iterable, Iterator, Callable, Sequence, Awaitable, AsyncIterator

from .stubborn_caller_async_iterator import StubbornCallerAsyncIterator
from .unfaltering_chaining_async_iterator import UnfalteringChainingAsyncIterator

T = TypeVar('T')

class CallChunkChainingAsyncIterator(Generic[T]):
    """Evaluate call chunks and chain them together."""

    @property
    def current_callable(self) -> Optional[Callable[[], Awaitable[Sequence[T]]]]:
        return self.__calling_itr.current

    @current_callable.setter
    def current_callable(self, value: Optional[Callable[[], Awaitable[Sequence[T]]]]) -> None:
        self.__calling_itr.current = value

    @property
    def current_iterator(self) -> Iterator[T]:
        return self.__chaining_itr.current_iterator

    @current_iterator.setter
    def current_iterator(self, value: Iterator[T]) -> None:
        self.__chaining_itr.current_iterator = value

    def __init__(self, chunks: Iterable[Callable[[], Awaitable[Sequence[T]]]]) -> None:
        self.__chunking_itr: Iterator[Callable[[], Awaitable[Sequence[T]]]] = iter(chunks)
        self.__calling_itr: StubbornCallerAsyncIterator[Sequence[T]] = StubbornCallerAsyncIterator(self.__chunking_itr)
        self.__chaining_itr: UnfalteringChainingAsyncIterator[T] = UnfalteringChainingAsyncIterator(self.__calling_itr)

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        return await self.__chaining_itr.__anext__()

    def get_chunking_iterator(self) -> Iterator[Callable[[], Awaitable[Sequence[T]]]]:
        return self.__chunking_itr
