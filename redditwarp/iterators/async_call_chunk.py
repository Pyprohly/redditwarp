
from __future__ import annotations
from typing import TypeVar, Callable, Generic, Awaitable

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

class AsyncCallChunk(Generic[TInput, TOutput]):
    """Perform `.operation` on `.operand` when called."""

    def __init__(self,
        operation: Callable[[TInput], Awaitable[TOutput]],
        operand: TInput,
    ) -> None:
        self.operation: Callable[[TInput], Awaitable[TOutput]] = operation
        ("")
        self.operand: TInput = operand
        ("")

    async def __call__(self) -> TOutput:
        return await self.operation(self.operand)
