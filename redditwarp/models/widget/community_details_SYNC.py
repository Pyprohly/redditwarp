
from __future__ import annotations

from dataclasses import dataclass

from .widget_SYNC import Widget

@dataclass(repr=False, eq=False)
class CommunityDetailsWidget(Widget):
    public_description: str
    subscriber_text: str
    viewing_text: str
    subscriber_count: int
    viewing_count: int
