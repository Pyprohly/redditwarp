
from __future__ import annotations

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class Rule:
    description: str
    description_html: str
    short_name: str
    violation_reason: str
    created_ut: int
