
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, ContextManager
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

        with except_without_context(PermissionError) as xcpt:
            raise PermissionError
        if xcpt:
            f()

    Result::

        LookupError
        The above exception was the direct cause of the following exception:
        KeyError

    Just right.
    """

    def __init__(self, *exceptions: Type[BaseException]):
        self.exceptions = exceptions
        self.yes = False

    def __bool__(self) -> bool:
        return self.yes

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        if exc_type is not None and issubclass(exc_type, self.exceptions):
            self.yes = True
        return True
