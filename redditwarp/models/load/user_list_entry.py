
from __future__ import annotations
from typing import Any, Mapping

from ..user_list_entry import UserListEntry, FriendUserListEntry

def load_user_list_entry(d: Mapping[str, Any]) -> UserListEntry:
    return UserListEntry(d)

def load_friend_user_list_entry(d: Mapping[str, Any]) -> FriendUserListEntry:
    return FriendUserListEntry(d)
