
from __future__ import annotations
from typing import Any, Mapping, Optional

from functools import cached_property
from datetime import datetime, timezone

class UserListEntry:
    def __init__(self, d: Mapping[str, Any]):
        self.d = d
        _full_id36: str = d['id']
        _, _, id36 = _full_id36.partition('_')
        self.id36 = id36
        self.id = int(id36, 36)
        self.name: str = d['name']
        self.rel_id: str = d['rel_id']
        self.added_ut = int(d['date'])

    @cached_property
    def added_at(self) -> datetime:
        return datetime.fromtimestamp(self.added_ut, timezone.utc)

class FriendUserListEntry(UserListEntry):
    def __init__(self, d: Mapping[str, Any]):
        self.note: Optional[str] = d['note']
