
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Mapping, Optional, Union, Any
if TYPE_CHECKING:
    from collections.abc import MutableSequence
    from types import TracebackType
    from .request import Request
    from .response import Response
    from .payload import RequestFiles

import contextvars
from collections import deque

from .requestor_ASYNC import Requestor
from .request import make_request

T = TypeVar('T')

DEFAULT_TIMEOUT: float = 100.

class SessionBase(Requestor):
    @staticmethod
    def make_request(
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
    ) -> Request:
        return make_request(
            verb,
            uri,
            params=params,
            headers=headers,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
        )

    def __init__(self) -> None:
        self.timeout: float = DEFAULT_TIMEOUT
        self._veto_timeout: contextvars.ContextVar[float] = contextvars.ContextVar('veto_timeout', default=-2.)

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        raise NotImplementedError

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
    ) -> Response:
        r = self.make_request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files)
        return await self.send(r, timeout=timeout)

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
        def __init__(self, veto_timeout: contextvars.ContextVar[float], timeout: float) -> None:
            self._veto_timeout = veto_timeout
            self._timeout = timeout
            self._reset_token_stack: MutableSequence[contextvars.Token[float]] = deque()

        def __enter__(self) -> None:
            tkn = self._veto_timeout.set(self._timeout)
            self._reset_token_stack.append(tkn)

        def __exit__(self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            exc_traceback: Optional[TracebackType],
        ) -> Optional[bool]:
            tkn = self._reset_token_stack.pop()
            self._veto_timeout.reset(tkn)
            return None

    def timeout_as(self, timeout: float) -> _TimeoutAsContextManager:
        return self._TimeoutAsContextManager(self._veto_timeout, timeout)
