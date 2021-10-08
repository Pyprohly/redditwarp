
from __future__ import annotations
from typing import Any, Mapping

from datetime import datetime, timezone

from .artifact import IArtifact

class ModLogActionEntry(IArtifact):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d = d
        self.action: str = d['action']
        self.mod: str = d['mod']
        self.mod_id36: str = d['mod_id36']
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
