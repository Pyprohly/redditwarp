
from __future__ import annotations
from typing import Any, Mapping

from ..subreddit_user_item import (
    ModeratorUserItem,
    ContributorUserItem,
    BannedUserItem,
    MutedUserItem,
)

def load_moderator_user_item(d: Mapping[str, Any]) -> ModeratorUserItem:
    return ModeratorUserItem(d)

def load_contributor_user_item(d: Mapping[str, Any]) -> ContributorUserItem:
    return ContributorUserItem(d)

def load_banned_user_item(d: Mapping[str, Any]) -> BannedUserItem:
    return BannedUserItem(d)

def load_muted_user_item(d: Mapping[str, Any]) -> MutedUserItem:
    return MutedUserItem(d)
