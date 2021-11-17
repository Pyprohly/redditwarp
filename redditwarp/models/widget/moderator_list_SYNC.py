
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .moderator_list import ModeratorInfo

from dataclasses import dataclass

from .widget_SYNC import Widget

@dataclass(repr=False, eq=False)
class ModeratorListWidget(Widget):
    mod_num: int
    mods: Sequence[ModeratorInfo]
