
from __future__ import annotations
from typing import TypeVar, AsyncIterable, Generic, AsyncIterator

T = TypeVar('T')

class UnfalteringChainingAsyncIterator(Generic[T]):
    """Like `itertools.chain.from_iterable()` but is able to continue when
    an exception occurs during iteration.

    Also has a `self.current_iter` attribute.
    """

    def __init__(self, iterable: AsyncIterable[AsyncIterable[T]]) -> None:
        self._iterator = iterable.__aiter__()
        async def f() -> AsyncIterator[T]:
            return
            yield
        self.current_iter: AsyncIterator[T] = f()

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        while True:
            async for element in self.current_iter:
                return element
            self.current_iter = (await self._iterator.__anext__()).__aiter__()
