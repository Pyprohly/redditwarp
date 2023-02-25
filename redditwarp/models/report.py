
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

        Unknown what happens if the user is deleted.
        Is the value `[deleted]`, an empty string, or does the field in the
        underlying object not exist?
        If you have any information about this, please open an issue report at
        `<https://github.com/Pyprohly/redditwarp/issues>`_.
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
