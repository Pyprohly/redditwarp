
from typing import Any, Mapping, Optional

from datetime import datetime
from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class ModerationNote(IArtifact):
    #_: KW_ONLY
    d: Mapping[str, Any]
    uuid: str
    timestamp: int
    datetime: datetime
    type: str
    subreddit_id: int
    subreddit: str
    agent_id: int
    agent: str
    target_id: int
    target: str

@dataclass(repr=False, eq=False)
class ModerationActionNote(ModerationNote):
    action: str

@dataclass(repr=False, eq=False)
class ModerationUserNote(ModerationNote):
    note: str
    label: str
    has_anchor: bool
    anchor_submission_id: Optional[int]
    anchor_comment_id: Optional[int]
