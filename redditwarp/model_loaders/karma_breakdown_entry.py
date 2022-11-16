
from __future__ import annotations
from typing import Any, Mapping

from ..models.karma_breakdown_entry import KarmaBreakdownEntry

def load_karma_breakdown_entry(d: Mapping[str, Any]) -> KarmaBreakdownEntry:
    return KarmaBreakdownEntry(
        sr=d['sr'],
        comment_karma=d['comment_karma'],
        submission_karma=d['link_karma'],
    )
