
from __future__ import annotations
from typing import TypeVar, Callable, Generic, Sequence

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

class CallChunk(Generic[TInput, TOutput]):
    """Call me to perform `.operation` on `.items` to produce products."""

    def __init__(self,
        operation: Callable[[Sequence[TInput]], Sequence[TOutput]],
        items: Sequence[TInput],
    ) -> None:
        self.operation = operation
        self.items = items

    def __call__(self) -> Sequence[TOutput]:
        return self.operation(self.items)
