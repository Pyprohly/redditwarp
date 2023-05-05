
from __future__ import annotations
from typing import Any, Mapping, Optional

from functools import cached_property
from datetime import datetime, timezone

class UserRelationship:
    @cached_property
    def added_at(self) -> datetime:
        """Datetime object of when the relationship was created."""
        return datetime.fromtimestamp(self.added_ut, timezone.utc)

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36: str = id36
        ("""
            User ID as a base 36 number.
            """)
        self.idn: int = int(id36, 36)
        ("""
            User ID.
            """)
        self.id: int = self.idn
        ("""
            Same as :attr:`idn`.
            """)
        self.name: str = d['name']
        ("""
            Username.
            """)
        #self.rel_id: str = d['rel_id']
        self.added_ut: int = int(d['date'])
        ("""
            UNIX timestamp of when the relationship was created.
            """)

class FriendRelationship(UserRelationship):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        # Need Reddit Premium to test this
        # self.note: str = d['note'] or ''

class BannedSubredditUserRelationship(UserRelationship):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.days_remaining: Optional[int] = d['days_left']
        ("""
            Number of days until the ban is lifted.

            Value `None` if the ban is permanent.
            """)
        self.reason: str = d['note']
        ("""
            Ban reason.
            """)
