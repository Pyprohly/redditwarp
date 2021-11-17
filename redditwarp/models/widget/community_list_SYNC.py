
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .community_list import CommunityListWidgetItem

from dataclasses import dataclass

from .widget_SYNC import Widget

@dataclass(repr=False, eq=False)
class CommunityListWidget(Widget):
    items: Sequence[CommunityListWidgetItem]
