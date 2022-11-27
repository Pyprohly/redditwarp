
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Mapping

from dataclasses import dataclass

from .exceptions import status_successful, raise_now, raise_for_status


@dataclass(repr=False, eq=False)
class Response:
    status: int
    headers: Mapping[str, str]
    data: bytes

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.status}]>"

    def status_successful(self) -> bool:
        return status_successful(self.status)

    def raise_now(self) -> None:
        raise_now(self.status)

    def raise_for_status(self) -> None:
        raise_for_status(self.status)

@dataclass(repr=False, eq=False)
class UResponse(Response):
    underlying_object: object = None
