
from __future__ import annotations
from typing import Any, Mapping, Collection

from functools import cached_property
from datetime import datetime, timezone

class ModeratorListItem:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36: str = id36
        ("""
            User ID of the moderator as a base 36 number.
            """)
        self.id: int = int(id36, 36)
        ("""
            User ID of the moderator.
            """)
        self.name: str = d['name']
        ("""
            The moderator's user name.
            """)
        #self.rel_id: str = d['rel_id']
        self.added_ut: int = int(d['date'])
        ("""
            Unix timestamp of when the user was added as a moderator.
            """)
        self.flair_text: str = d['author_flair_text']
        ("""
            The moderator's flair text.
            """)
        self.flair_css_class: str = d['author_flair_css_class']
        ("""
            The moderator's flair CSS class.
            """)
        self.permissions: Collection[str] = d['mod_permissions']
        ("""
            Values: `all`, `access`, `chat_config`, `chat_operator`, `config`, `flair`, `mail`, `posts`, `wiki`.
            """)

    @cached_property
    def added_at(self) -> datetime:
        """Datetime object of when the user was added as a moderator."""
        return datetime.fromtimestamp(self.added_ut, timezone.utc)
