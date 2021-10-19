
from __future__ import annotations
from typing import TypeVar, Callable, Generic

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

class CallChunk(Generic[TInput, TOutput]):
    """Perform `.operation` on `.operand` when called."""

    def __init__(self,
        operation: Callable[[TInput], TOutput],
        operand: TInput,
    ) -> None:
        self.operation = operation
        self.operand = operand

    def __call__(self) -> TOutput:
        return self.operation(self.operand)
