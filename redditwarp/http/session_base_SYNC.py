
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Mapping, Optional, Union, Any
if TYPE_CHECKING:
    from collections.abc import MutableSequence
    from types import TracebackType
    from contextlib import AbstractContextManager
    from .request import Request
    from .response import Response
    from .payload import RequestFiles

import contextvars
from collections import deque

from .requestor_SYNC import Requestor
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
    ) -> Request:
        return make_request(
            verb,
            uri,
            params=params,
            headers=headers,
            data=data,
            json=json,
            files=files,
        )

    def __init__(self) -> None:
        self.timeout: float = DEFAULT_TIMEOUT
        self.follow_redirects: bool = False
        self.___veto_timeout: contextvars.ContextVar[float] = contextvars.ContextVar('___veto_timeout', default=-2.)

    def __enter__(self: T) -> T:
        return self

    def __exit__(self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        """
        .. PARAMETERS

        :param request:
            The request to send.
        :param timeout:
            A timeout value for the total exchange.

            A value of `0` has no special meaning.
            A :class:`~.exceptions.TimeoutException` will be raised immediately.

            A value of `-1` means infinite timeout.

            A value of `-2` means use the session default.

        .. RAISES

        :raises ValueError:
            An invalid timeout value was specified.
        """
        raise NotImplementedError

    def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        data: Optional[Union[Mapping[str, str], bytes]] = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = -2,
        follow_redirects: Optional[bool] = None,
    ) -> Response:
        r = self.make_request(verb, uri, params=params, headers=headers,
                data=data, json=json, files=files)
        return self.send(r, timeout=timeout, follow_redirects=follow_redirects)

    def close(self) -> None:
        pass

    def ___get_effective_timeout_value(self, timeout: float) -> float:
        t1 = self.___veto_timeout.get()
        t2 = timeout
        t3 = self.timeout
        for tv in (t1, t2, t3):
            if tv == -2:
                continue
            if 0 > tv != -1:
                raise ValueError('invalid timeout value: %s' % tv)
            return tv
        raise ValueError('a default timeout value could not be determined')

    class ___TimeoutAsContextManager:
        def __init__(self, var: contextvars.ContextVar[float], timeout: float) -> None:
            self._var = var
            self._timeout = timeout
            self._token_stack: MutableSequence[contextvars.Token[float]] = deque()

        def __enter__(self) -> None:
            tkn = self._var.set(self._timeout)
            self._token_stack.append(tkn)

        def __exit__(self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            exc_traceback: Optional[TracebackType],
        ) -> Optional[bool]:
            tkn = self._token_stack.pop()
            self._var.reset(tkn)
            return None

    def ___timeout_as(self, timeout: float) -> AbstractContextManager[None]:
        return self.___TimeoutAsContextManager(self.___veto_timeout, timeout)
