
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Mapping

from dataclasses import dataclass


@dataclass(repr=False, eq=False)
class Request:
    verb: str
    url: str
    headers: Mapping[str, str]
    data: bytes

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{self.verb}]>"
