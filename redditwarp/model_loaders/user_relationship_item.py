
from __future__ import annotations
from typing import Any, Mapping

from ..models.user_relationship_item import UserRelationshipItem, FriendRelationshipItem, BannedUserRelationshipItem

def load_user_relationship_item(d: Mapping[str, Any]) -> UserRelationshipItem:
    return UserRelationshipItem(d)

def load_friend_relationship_item(d: Mapping[str, Any]) -> FriendRelationshipItem:
    return FriendRelationshipItem(d)

def load_banned_user_relation_item(d: Mapping[str, Any]) -> BannedUserRelationshipItem:
    return BannedUserRelationshipItem(d)
