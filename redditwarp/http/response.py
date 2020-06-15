
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Any
    from collections.abc import Mapping
    from .request import Request

from dataclasses import dataclass
from .exceptions import raise_now, raise_for_status

@dataclass(eq=False)
class Response:
    status: int
    headers: Mapping[str, str]
    data: bytes
    request: Optional[Request] = None
    underlying_object: Any = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} [{self.status}]>'

    def raise_now(self) -> None:
        raise_now(self)

    def raise_for_status(self) -> None:
        raise_for_status(self)
