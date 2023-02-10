
from typing import Any, Mapping

from datetime import datetime
from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class ModerationActionLogEntry(IArtifact):
    #_: KW_ONLY
    d: Mapping[str, Any]
    uuid: str
    ("""
        Mod action unique identifier.
        """)
    unixtime: int
    ("""
        Unix timestamp of when the action was performed.
        """)
    datetime: datetime
    ("""
        Datetime object of when the action was performed.
        """)
    action: str
    ("""
        Name of the moderation action.
        """)
    agent_id: int
    ("""
        ID of the moderator who initiated the action.
        """)
    agent: str
    ("""
        Name of the moderator who initiated the action.
        """)
