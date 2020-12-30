
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from typing import ClassVar, Optional, Type, Any
    from types import TracebackType
    from collections.abc import Mapping
    from .request import Request
    from .response import Response
    from .transporter_info import TransporterInfo

from .transporter_info import blank_transporter
from .requestor_ASYNC import Requestor

T = TypeVar('T')

class BaseSession(Requestor):
    TRANSPORTER_INFO: ClassVar[TransporterInfo] = blank_transporter

    def __init__(self,
        *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float = 60,
    ) -> None:
        self.params = {} if params is None else params
        self.headers = {} if headers is None else headers
        self.timeout = timeout

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    def _prepare_request(self, request: Request) -> None:
        h = request.headers
        h.update({**self.headers, **h})
        p = request.params
        p.update({**self.params, **p})

    async def send(self, request: Request, *, timeout: float = 0,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        raise NotImplementedError

    async def close(self) -> None:
        pass
