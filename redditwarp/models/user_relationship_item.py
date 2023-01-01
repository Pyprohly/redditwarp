
from __future__ import annotations
from typing import Any, Mapping, Optional

from functools import cached_property
from datetime import datetime, timezone

class UserRelationshipItem:
    @cached_property
    def added_at(self) -> datetime:
        return datetime.fromtimestamp(self.added_ut, timezone.utc)

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36: str = id36
        self.id: int = int(id36, 36)
        self.name: str = d['name']
        #self.rel_id: str = d['rel_id']
        self.added_ut: int = int(d['date'])

class FriendRelationshipItem(UserRelationshipItem):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        # Need premium to test this
        #self.note: Optional[str] = d['note']

class BannedUserRelationshipItem(UserRelationshipItem):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.days_remaining: Optional[int] = d['days_left']
        self.detail: str = d['note']
