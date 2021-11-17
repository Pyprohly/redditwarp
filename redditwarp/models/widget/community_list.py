
from __future__ import annotations

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class CommunityListWidgetItem:
    name: str
    subscribers: int
    icon_img: str
    community_icon: str
    primary_color: str
    nsfw: bool
