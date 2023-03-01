
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Mapping

from dataclasses import dataclass

from .exceptions import is_successful_status, raise_now, ensure_successful_status


@dataclass(repr=False, eq=False)
class Response:
    status: int
    headers: Mapping[str, str]
    data: bytes

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.status}]>"

    def is_successful_status(self) -> bool:
        """Return true if `200 <= self.status <= 299`."""
        return is_successful_status(self.status)

    def raise_now(self) -> None:
        """Raises a :class:`~.http.exceptions.StatusCodeException` exception type based on the `.status` number."""
        raise_now(self.status)

    def ensure_successful_status(self) -> None:
        """Raises a :class:`~.http.exceptions.StatusCodeException` exception if `.is_successful_status()` returns false."""
        ensure_successful_status(self.status)


@dataclass(repr=False, eq=False)
class UResponse(Response):
    underlying_object: object = None
