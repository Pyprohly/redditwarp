
from __future__ import annotations
from typing import Mapping, Any

from enum import IntEnum
from dataclasses import dataclass

from .artifact import IArtifact

class ConversationProgress(IntEnum):
    NEW = 0
    IN_PROGRESS = 1
    ARCHIVED = 2

class ModmailModActionType(IntEnum):
    HIGHLIGHT = 0
    UNHIGHLIGHT = 1
    ARCHIVE = 2
    UNARCHIVE = 3
    MUTE_USER = 5
    UNMUTE_USER = 6
    BAN_USER = 7
    UNBAN_USER = 8
    APPROVE_USER = 9
    DISAPPROVE_USER = 10


@dataclass(repr=False, eq=False)
class ModmailModeratedSubreddit(IArtifact):
    d: Mapping[str, Any]
    id: int
    name: str
    subscriber_count: int
