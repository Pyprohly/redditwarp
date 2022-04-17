
from typing import Any, Mapping

from datetime import datetime
from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class ModerationActionLogEntry(IArtifact):
    #_: KW_ONLY
    d: Mapping[str, Any]
    uuid: str
    timestamp: int
    datetime: datetime
    action: str
    agent_id: int
    agent: str
