
from __future__ import annotations
from typing import Any, Mapping

from ..models.user_relationship import UserRelationship, FriendRelationship, BannedSubredditUserRelationship

def load_user_relationship(d: Mapping[str, Any]) -> UserRelationship:
    return UserRelationship(d)

def load_friend_relationship(d: Mapping[str, Any]) -> FriendRelationship:
    return FriendRelationship(d)

def load_banned_subreddit_user_relation(d: Mapping[str, Any]) -> BannedSubredditUserRelationship:
    return BannedSubredditUserRelationship(d)
