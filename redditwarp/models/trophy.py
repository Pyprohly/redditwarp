
from __future__ import annotations
from typing import Any, Mapping

from .artifact import Artifact

class Trophy(Artifact):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.name: str = d['name']
        self.icon_40: str = d['icon_40']
        self.icon_70: str = d['icon_70']
        self.description: str = d['description'] or ''
