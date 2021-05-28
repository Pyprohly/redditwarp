
from __future__ import annotations
from typing import Any, Mapping

from ..karma_breakdown_entry import KarmaBreakdownEntry

def load_karma_breakdown_entry(d: Mapping[str, Any]) -> KarmaBreakdownEntry:
    sr_name = d['sr']
    comment_karma = d['comment_karma']
    submission_karma = d['link_karma']
    return KarmaBreakdownEntry(sr_name, comment_karma, submission_karma)
