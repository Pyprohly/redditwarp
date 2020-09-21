
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .funbox import FunBox

class OriginalRedditThingObject(FunBox):
    THING_PREFIX = ''

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.id36: str = d['id']
        self.id = int(self.id36, 36)
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id36={self.id36!r}>'
