
from __future__ import annotations
from typing import Any, Mapping

from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class Trophy(IArtifact):
    d: Mapping[str, Any]
    name: str
    description: str
    icon_40: str
    icon_70: str
