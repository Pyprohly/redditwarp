
from __future__ import annotations

from enum import Enum, auto

class CommentMessageCause(Enum):
    USERNAME_MENTION = auto()
    SUBMISSION_REPLY = auto()
    COMMENT_REPLY = auto()
