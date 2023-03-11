
from __future__ import annotations
from typing import Any, Mapping, Optional

from functools import cached_property
from datetime import datetime, timezone

class SubredditUser:
    @cached_property
    def added_at(self) -> datetime:
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
        self.id: int = int(id36, 36)
        ("""
            User ID.
            """)
        self.name: str = d['username']
        ("""
            Username.
            """)
        self.account_icon: str = d['accountIcon']
        ("""
            URL of the user account's icon.
            """)
        self.icon_size: tuple[int, int] = d['iconSize']
        ("""
            Usually `(256, 256)`.
            """)
        self.added_ut: int = 0
        ("")

class Moderator(SubredditUser):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['moddedAtUTC']
        ("""
            UNIX timestamp of when the user added as a moderator.
            """)
        self.flair_text: str = d['authorFlairText']
        ("""
            The flair text of the moderator.
            """)
        self.permissions: set[str] = {k for k, v in d['modPermissions'].items() if v}
        ("""
            Values: `all`, `wiki`, `chat_operator`, `chat_config`,
            `posts`, `access`, `mail`, `config`, `flair`.
            """)
        self.post_karma: int = d['postKarma']
        ("")

class ApprovedUser(SubredditUser):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['approvedAtUTC']
        ("""
            UNIX timestamp of when the user added as an approved user.
            """)

class BannedUser(SubredditUser):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['bannedAtUTC']
        ("""
            UNIX timestamp of when the user was banned.
            """)
        self.agent_name: str = d['bannedBy']
        ("""
            Name of the moderator who banned the user.

            Unknown what happens if the user is deleted.
            Is the value `[deleted]`, an empty string, or does the field in the
            underlying object not exist?
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        self.reason: str = d['reason'] or ''
        ("""
            Ban reason.
            """)
        self.note: str = d['modNote'] or ''
        ("""
            A moderator note.
            """)
        self.message: str = d['banMessage']
        ("""
            The message that was sent to the user when they were banned.
            """)
        self.days_remaining: Optional[int] = d['duration']
        ("""
            Number of days until the ban is lifted.

            Value `None` if the ban is permanent.
            """)

class MutedUser(SubredditUser):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.added_ut: int = d['mutedAtUTC']
        ("""
            UNIX timestamp of when the user was muted.
            """)
        self.agent_name: str = d['mutedBy']
        ("""
            Name of the moderator who muted the user.

            Unknown what happens if the user is deleted.
            Is the value `[deleted]`, an empty string, or does the field in the
            underlying object not exist?
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        self.reason: str = d['reason']
        ("""
            A moderator note.
            """)
