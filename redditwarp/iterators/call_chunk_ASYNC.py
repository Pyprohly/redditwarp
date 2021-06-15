
from __future__ import annotations
from typing import TypeVar, Callable, Generic, Sequence, Awaitable

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

class CallChunk(Generic[TInput, TOutput]):
    def __init__(self,
        operation: Callable[[Sequence[TInput]], Awaitable[Sequence[TOutput]]],
        items: Sequence[TInput],
    ) -> None:
        self.operation = operation
        self.items = items

    async def __call__(self) -> Sequence[TOutput]:
        return await self.operation(self.items)
