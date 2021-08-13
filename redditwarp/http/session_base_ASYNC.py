
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import Optional, Type
    from collections.abc import MutableSequence
    from types import TracebackType
    from .request import Request
    from .response import Response

import contextvars
from collections import deque

from .requestor_ASYNC import Requestor
from .request import make_request

T = TypeVar('T')

DEFAULT_TIMEOUT = 100.

class SessionBase(Requestor):
    make_request = staticmethod(make_request)

    def __init__(self) -> None:
        self.timeout: float = DEFAULT_TIMEOUT
        self._veto_timeout: contextvars.ContextVar[float] = contextvars.ContextVar('veto_timeout', default=-2.)

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        raise NotImplementedError

    async def close(self) -> None:
        pass

    def _get_effective_timeout_value(self, timeout: float) -> float:
        t1 = self._veto_timeout.get()
        t2 = timeout
        t3 = self.timeout
        for tv in (t1, t2, t3):
            if tv == -2:
                continue
            if 0 > tv != -1:
                raise ValueError('invalid timeout value: %s' % tv)
            return tv
        raise ValueError('a default timeout value could not be determined')

    class _TimeoutAsContextManager:
        def __init__(self, subject: SessionBase, timeout: float) -> None:
            self._subject = subject
            self._timeout = timeout
            self._veto_timeout = subject._veto_timeout
            self._reset_token_stack: MutableSequence[contextvars.Token[float]] = deque()

        def __enter__(self) -> None:
            self._reset_token_stack.append(self._veto_timeout.set(self._timeout))

        def __exit__(self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
        ) -> Optional[bool]:
            token = self._reset_token_stack.pop()
            self._veto_timeout.reset(token)
            return None

    def timeout_as(self, timeout: float) -> _TimeoutAsContextManager:
        return self._TimeoutAsContextManager(self, timeout)
