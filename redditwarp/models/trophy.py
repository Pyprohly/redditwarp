
from __future__ import annotations
from typing import Any, Mapping, Optional

from datetime import datetime, timezone

class Trophy:
    def __init__(self, d: Mapping[str, Any]):
        self.d = d
        self.id36: Optional[str] = d['id']
        self.name: str = d['name']
        self.award_id: Optional[str] = d['award_id']
        self.added_ut = int(d['date'])
        self.description: str = d['description']
        self.url: Optional[str] = d['url']
        self.icon_40: str = d['icon_40']
        self.icon_70: str = d['icon_70']
        self.granted_ut: Optional[int] = d['granted_ut']
        self.granted_at: Optional[datetime] = None
        if self.granted_ut is not None:
            self.granted_at = datetime.fromtimestamp(self.granted_ut, timezone.utc)
