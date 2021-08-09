
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import Optional, Type, Any
    from types import TracebackType
    from collections.abc import Mapping
    from .request import Request
    from .response import Response

from .requestor_SYNC import Requestor
from .request import make_request

T = TypeVar('T')

DEFAULT_TIMEOUT = 100.

class SessionBase(Requestor):
    make_request = staticmethod(make_request)

    def __init__(self) -> None:
        self.timeout: float = DEFAULT_TIMEOUT

    def __enter__(self: T) -> T:
        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def send(self, request: Request, *, timeout: float = -2,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        """
        Parameters
        ----------
        timeout: Optional[float]
            The connect timeout. The number of seconds the client will
            wait to establish a connection to the server.

            A None value will use a default that is specific to the transport
            adaptor. A negative number will wait an infinite amount of time.
        aux_info: Optional[Mapping[Any, Any]]
            Additional information to be consumed by a custom :class:`SessionBase` class.
        """
        raise NotImplementedError

    def close(self) -> None:
        pass
