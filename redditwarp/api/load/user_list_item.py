
from __future__ import annotations
from typing import Any, Mapping

from ...models.user_list_item import UserListItem

def load_user_list_item(d: Mapping[str, Any]) -> UserListItem:
    return UserListItem(d)
