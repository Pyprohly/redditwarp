
from __future__ import annotations

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class ModeratorInfo:
    name: str
    flair_type: str
    flair_text: str
    flair_fg_light_or_dark: str
    flair_bg_color: str
    flair_has_had_flair: bool
