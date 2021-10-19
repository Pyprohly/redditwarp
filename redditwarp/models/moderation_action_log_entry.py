
from __future__ import annotations
from typing import Any, Mapping

from datetime import datetime, timezone

from .artifact import IArtifact

class ModerationActionLogEntry(IArtifact):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d = d
        self.action_name: str = d['action']
        self.agent_name: str = d['mod']
        self.agent_id = int(d['mod_id36'], 36)
        self.timestamp = int(d['created_utc'])
        self.datetime = datetime.fromtimestamp(self.timestamp, timezone.utc)
