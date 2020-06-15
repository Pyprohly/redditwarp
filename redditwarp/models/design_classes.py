"""Artifical class constructs that reflect the design model of some Reddit objects.
"""

from __future__ import annotations
from typing import Mapping, Any

from .object import FunBox

class Thing(FunBox):
    THING_PREFIX = ''

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.id36 = id36 = d['id']
        self.id = int(id36, 36)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id36={self.id36!r}>'
