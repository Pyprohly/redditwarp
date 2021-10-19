
from __future__ import annotations
from typing import Any, Mapping

import sys
from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class Trophy(IArtifact):
    d: Mapping[str, Any]
    name: str
    description: str
    icon_40: str
    icon_70: str

    if sys.version_info[:3] == (3, 9, 7):
        # https://bugs.python.org/issue45081
        def __init__(self,
            d: Mapping[str, Any],
            name: str,
            description: str,
            icon_40: str,
            icon_70: str,
        ) -> None:
            self.d = d
            self.name = name
            self.description = description
            self.icon_40 = icon_40
            self.icon_70 = icon_70
