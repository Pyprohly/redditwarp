
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, ContextManager
if TYPE_CHECKING:
    from types import TracebackType

class except_without_context(ContextManager[bool]):
    def __init__(self, *exceptions: Type[BaseException]):
        self._exceptions = exceptions
        self.yes = False

    def __bool__(self) -> bool:
        return self.yes

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        if exc_type is not None and issubclass(exc_type, self._exceptions):
            self.yes = True
        return True
