
from __future__ import annotations
from typing import Any, Mapping

from datetime import datetime, timezone

from ..models.moderation_action_log_entry import ModerationActionLogEntry

def load_moderation_action_log_entry(d: Mapping[str, Any]) -> ModerationActionLogEntry:
    return ModerationActionLogEntry(
        d=d,
        uuid=d['id'].partition('_')[-1],
        unixtime=(unixtime := int(d['created_utc'])),
        datetime=datetime.fromtimestamp(unixtime, timezone.utc),
        action=d['action'],
        agent_id=int(d['mod_id36'], 36),
        agent=d['mod'],
    )
