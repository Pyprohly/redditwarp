
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, ContextManager
if TYPE_CHECKING:
    from types import TracebackType

class except_without_context(ContextManager[bool]):
    """
    Example 1::

        def f() -> None:
            try:
                raise LookupError
            except LookupError as e:
                raise KeyError from e

        try:
            raise PermissionError
        except PermissionError as e:
            f()

    Result::

        PermissionError
        During handling of the above exception, another exception occurred:
        LookupError
        The above exception was the direct cause of the following exception:
        KeyError

    We don't want PermissionError to show.


    Example 2::

        try:
            raise PermissionError
        except PermissionError as e:
            try:
                f()
            except Exception as e:
                raise e from None

    Result::

        KeyError

    LookupError is missing.


    Example 3::

        with except_without_context(PermissionError) as ewc:
            raise PermissionError
        if ewc:
            f()

    Result::

        LookupError
        The above exception was the direct cause of the following exception:
        KeyError

    Just right.
    """

    def __init__(self, *exceptions: type[BaseException]):
        self.exceptions: tuple[type[BaseException], ...] = exceptions
        self.yes: bool = False

    def __bool__(self) -> bool:
        return self.yes

    def __exit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.yes = exc_type is not None and issubclass(exc_type, self.exceptions)
        return True
