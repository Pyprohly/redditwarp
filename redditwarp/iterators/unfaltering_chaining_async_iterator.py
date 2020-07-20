
from __future__ import annotations
from typing import TypeVar, AsyncIterable, Iterable, AsyncIterator, Iterator

T = TypeVar('T')

class UnfalteringChainingAsyncIterator(AsyncIterator[T]):
    def __init__(self, source: AsyncIterable[Iterable[T]]) -> None:
        self._iterator = source.__aiter__()
        self.current_iter: Iterator[T] = iter(())

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        while True:
            for link in self.current_iter:
                return link
            it = await self._iterator.__anext__()
            try:
                self.current_iter = iter(it)
            except StopIteration:
                raise StopAsyncIteration
