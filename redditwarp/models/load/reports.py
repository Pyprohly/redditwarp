
from __future__ import annotations
from typing import Any, Sequence

from ..reports import ModReport, UserReport

def load_mod_report(arr: Sequence[Any]) -> ModReport:
    reason, agent_name = arr
    return ModReport(
        reason=reason,
        agent_name=agent_name,
    )

def load_user_report(arr: Sequence[Any]) -> UserReport:
    reason, count, snoozed, can_snooze = arr
    return UserReport(
        reason=reason,
        count=count,
        snoozed=snoozed,
        can_snooze=can_snooze,
    )
