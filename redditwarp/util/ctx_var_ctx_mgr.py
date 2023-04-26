
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableSequence, ContextManager, TypeVar
if TYPE_CHECKING:
    from types import TracebackType

from contextvars import ContextVar, Token
from collections import deque

T = TypeVar('T')

class ContextVarContextManager(ContextManager[None]):
    def __init__(self, ctx_var: ContextVar[T], var_val: T) -> None:
        self._ctx_var: ContextVar[T] = ctx_var
        self._var_val: T = var_val
        self._token_stack: MutableSequence[Token[T]] = deque()

    def __enter__(self) -> None:
        self._token_stack.append(self._ctx_var.set(self._var_val))

    def __exit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self._ctx_var.reset(self._token_stack.pop())
        return None
