
from __future__ import annotations
from typing import Any, Mapping

from ..user_list_item import UserListItem, FriendUserListItem

def load_user_list_item(d: Mapping[str, Any]) -> UserListItem:
    return UserListItem(d)

def load_friend_user_list_item(d: Mapping[str, Any]) -> FriendUserListItem:
    return FriendUserListItem(d)
