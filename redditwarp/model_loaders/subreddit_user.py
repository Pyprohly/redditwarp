
from __future__ import annotations
from typing import Any, Mapping

from ..models.subreddit_user import (
    Moderator,
    ApprovedUser,
    BannedUser,
    MutedUser,
)

def load_moderator(d: Mapping[str, Any]) -> Moderator:
    return Moderator(d)

def load_approved_user(d: Mapping[str, Any]) -> ApprovedUser:
    return ApprovedUser(d)

def load_banned_user(d: Mapping[str, Any]) -> BannedUser:
    return BannedUser(d)

def load_muted_user(d: Mapping[str, Any]) -> MutedUser:
    return MutedUser(d)
