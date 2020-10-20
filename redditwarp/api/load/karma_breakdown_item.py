
from __future__ import annotations
from typing import Any, Mapping

from ...models.karma_breakdown_item import KarmaBreakdownItem

def load_karma_breakdown_item(d: Mapping[str, Any]) -> KarmaBreakdownItem:
    sr_name = d['sr']
    comment_karma = d['comment_karma']
    submission_karma = d['link_karma']
    return KarmaBreakdownItem(sr_name, comment_karma, submission_karma)
