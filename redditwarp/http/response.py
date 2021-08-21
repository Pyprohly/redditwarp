
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from collections.abc import MutableMapping
    from .request import Request

from dataclasses import dataclass
from .exceptions import raise_now, raise_for_status

@dataclass(eq=False)
class Response:
    status: int
    headers: MutableMapping[str, str]
    data: bytes
    request: Optional[Request] = None
    underlying_object: object = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} [{self.status}]>'

    def raise_now(self) -> None:
        raise_now(self)

    def raise_for_status(self) -> None:
        raise_for_status(self)
