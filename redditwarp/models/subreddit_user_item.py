
from __future__ import annotations
from typing import Any, Mapping, Optional, cast

from functools import cached_property
from datetime import datetime, timezone

class SubredditUserItem:
    @cached_property
    def added_at(self) -> datetime:
        return datetime.fromtimestamp(self.added_ut, timezone.utc)

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36: str = id36
        self.id: int = int(id36, 36)
        self.name: str = d['username']
        self.account_icon: str = d['accountIcon']
        self.icon_size: tuple[int, int] = cast("tuple[int, int]", d['iconSize'])
        self.added_ut: int = 0

class ModeratorUserItem(SubredditUserItem):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['moddedAtUTC']
        self.flair_text: str = d['authorFlairText']
        self.permissions: set[str] = {k for k, v in d['modPermissions'].items() if v}
        self.post_karma: int = d['postKarma']

class ApprovedUserItem(SubredditUserItem):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['approvedAtUTC']

class BannedUserItem(SubredditUserItem):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['bannedAtUTC']
        self.agent_name: str = d['bannedBy']
        self.reason: str = d['reason'] or ''
        self.note: str = d['modNote'] or ''
        self.ban_message: str = d['banMessage']
        self.days_remaining: Optional[int] = d['duration']

class MutedUserItem(SubredditUserItem):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['mutedAtUTC']
        self.agent_name: str = d['mutedBy']
        self.reason: str = d['reason']
