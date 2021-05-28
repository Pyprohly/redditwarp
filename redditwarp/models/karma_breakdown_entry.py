
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class KarmaBreakdownEntry:
    sr_name: str
    comment_karma: int
    submission_karma: int
