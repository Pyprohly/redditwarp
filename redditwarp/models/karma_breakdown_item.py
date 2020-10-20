
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class KarmaBreakdownItem:
    sr_name: str
    comment_karma: int
    submission_karma: int
