
from __future__ import annotations
from typing import Any, Mapping

from datetime import datetime, timezone

from ..models.moderation_action_log_entry import ModerationActionLogEntry

def load_moderation_action_log_entry(d: Mapping[str, Any]) -> ModerationActionLogEntry:
    timestamp = int(d['created_utc'])
    return ModerationActionLogEntry(
        d=d,
        uuid=d['id'].partition('_')[-1],
        timestamp=timestamp,
        datetime=datetime.fromtimestamp(timestamp, timezone.utc),
        action=d['action'],
        agent_id=int(d['mod_id36'], 36),
        agent=d['mod'],
    )
