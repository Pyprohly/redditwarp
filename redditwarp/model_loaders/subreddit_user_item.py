
from __future__ import annotations
from typing import Any, Mapping

from ..models.subreddit_user_item import (
    ModeratorUserItem,
    ApprovedUserItem,
    BannedUserItem,
    MutedUserItem,
)

def load_moderator_user_item(d: Mapping[str, Any]) -> ModeratorUserItem:
    return ModeratorUserItem(d)

def load_approved_user_item(d: Mapping[str, Any]) -> ApprovedUserItem:
    return ApprovedUserItem(d)

def load_banned_user_item(d: Mapping[str, Any]) -> BannedUserItem:
    return BannedUserItem(d)

def load_muted_user_item(d: Mapping[str, Any]) -> MutedUserItem:
    return MutedUserItem(d)
