
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class ModReport:
    """A moderator report."""

    reason: str
    ("""
        Report reason provided by the moderator.
        """)
    agent_name: str
    ("""
        Name of the reporting moderator.
        """)

@dataclass
class UserReport:
    """An arbitrary user report."""

    reason: str
    ("""
        Report reason.
        """)
    count: int
    ("""
        Number of duplicate reports for this reason.
        """)
    snoozed: bool
    ("""
        Whether this report reason is snoozed.
        """)
    can_snooze: bool
