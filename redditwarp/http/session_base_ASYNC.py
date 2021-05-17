
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
from .requestor_ASYNC import Requestor
from .request import make_request

T = TypeVar('T')

class SessionBase(Requestor):
    TRANSPORTER_INFO: ClassVar[TransporterInfo] = BLANK_TRANSPORTER

    make_request = staticmethod(make_request)

    def __init__(self) -> None:
        self.default_timeout: float = 60

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def send(self, request: Request, *, timeout: float = -2,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        raise NotImplementedError

    async def close(self) -> None:
        pass
