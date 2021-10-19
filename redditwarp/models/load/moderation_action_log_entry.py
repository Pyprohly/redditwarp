
from __future__ import annotations
from typing import Any, Mapping

from ..moderation_action_log_entry import ModerationActionLogEntry

def load_mod_log_action_entry(d: Mapping[str, Any]) -> ModerationActionLogEntry:
    return ModerationActionLogEntry(d)
