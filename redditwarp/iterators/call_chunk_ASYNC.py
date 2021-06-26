
from __future__ import annotations
from typing import TypeVar, Callable, Generic, Awaitable

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

class CallChunk(Generic[TInput, TOutput]):
    def __init__(self,
        operation: Callable[[TInput], Awaitable[TOutput]],
        data: TInput,
    ) -> None:
        self.operation = operation
        self.data = data

    async def __call__(self) -> TOutput:
        return await self.operation(self.data)
