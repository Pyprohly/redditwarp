
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import ClassVar, Optional, Type, Any
    from types import TracebackType
    from collections.abc import Mapping
    from .request import Request
    from .response import Response
    from .transporter_info import TransporterInfo

from .transporter_info import BLANK_TRANSPORTER
from .requestor_SYNC import Requestor

T = TypeVar('T')

class BaseSession(Requestor):
    TRANSPORTER_INFO: ClassVar[TransporterInfo] = BLANK_TRANSPORTER

    def __init__(self, *, timeout: float = 60) -> None:
        self.timeout = timeout

    def __enter__(self: T) -> T:
        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()
        return None

    def send(self, request: Request, *, timeout: float = 0,
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
            Additional information to be consumed by a custom :class:`BaseSession` class.
        """
        raise NotImplementedError

    def close(self) -> None:
        pass
