
from __future__ import annotations
from typing import TypeVar, Callable, Generic, Awaitable, Sequence

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

def new_call_chunk_of_sequences(
    operation: Callable[[Sequence[TInput]], Awaitable[Sequence[TOutput]]],
    data: Sequence[TInput],
) -> CallChunk[Sequence[TInput], Sequence[TOutput]]:
    return CallChunk(operation, data)
