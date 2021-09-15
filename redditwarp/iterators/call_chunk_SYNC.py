
from __future__ import annotations
from typing import TypeVar, Callable, Generic

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

class CallChunk(Generic[TInput, TOutput]):
    """Perform `.operation` on `.data` when called."""

    def __init__(self,
        operation: Callable[[TInput], TOutput],
        data: TInput,
    ) -> None:
        self.operation = operation
        self.data = data

    def __call__(self) -> TOutput:
        return self.operation(self.data)
