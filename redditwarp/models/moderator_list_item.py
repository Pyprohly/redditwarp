
from __future__ import annotations
from typing import Any, Mapping, Collection

from functools import cached_property
from datetime import datetime, timezone

class ModeratorListItem:
    def __init__(self, d: Mapping[str, Any]):
        self.d = d
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36 = id36
        self.id = int(id36, 36)
        self.name: str = d['name']
        #self.rel_id: str = d['rel_id']
        self.added_ut = int(d['date'])
        self.flair_text: str = d['author_flair_text']
        self.flair_css_class: str = d['author_flair_css_class']
        self.permissions: Collection[str] = d['mod_permissions']

    @cached_property
    def added_at(self) -> datetime:
        return datetime.fromtimestamp(self.added_ut, timezone.utc)
