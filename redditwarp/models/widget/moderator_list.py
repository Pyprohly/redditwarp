
from __future__ import annotations

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class ModeratorInfo:
    @dataclass(repr=False, eq=False)
    class Flair:
        text_mode: str
        text: str
        bg_color: str
        fg_color_scheme: str
        has_had_flair_assigned_before_in_subreddit: bool

    name: str
    flair: Flair
