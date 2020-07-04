
from __future__ import annotations
from typing import TypeVar, AsyncIterable, Generic, AsyncIterator

T = TypeVar('T')

class UnfalteringChainingAsyncIterator(Generic[T]):
    def __init__(self, source: AsyncIterable[AsyncIterable[T]]) -> None:
        self._iterator = source.__aiter__()
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
