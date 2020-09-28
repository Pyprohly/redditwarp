
from __future__ import annotations
from typing import TypeVar, AsyncIterable, Iterable, AsyncIterator, Iterator

E = TypeVar('E')

class UnfalteringChainingAsyncIterator(AsyncIterator[E]):
    def __init__(self, source: AsyncIterable[Iterable[E]]) -> None:
        self._iterator = source.__aiter__()
        self.current_iter: Iterator[E] = iter(())

    def __aiter__(self) -> AsyncIterator[E]:
        return self

    async def __anext__(self) -> E:
        while True:
            for elem in self.current_iter:
                return elem
            it = await self._iterator.__anext__()
            try:
                self.current_iter = iter(it)
            except StopIteration:
                raise StopAsyncIteration
