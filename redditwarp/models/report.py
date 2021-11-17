
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class ModReport:
    reason: str
    agent_name: str

@dataclass
class UserReport:
    reason: str
    count: int
    snoozed: bool
    can_snooze: bool
