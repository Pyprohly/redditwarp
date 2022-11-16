
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class KarmaBreakdownEntry:
    sr: str
    comment_karma: int
    submission_karma: int
