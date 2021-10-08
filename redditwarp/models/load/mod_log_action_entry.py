
from __future__ import annotations
from typing import Any, Mapping

from ..mod_log_action_entry import ModLogActionEntry

def load_mod_log_action_entry(d: Mapping[str, Any]) -> ModLogActionEntry:
    return ModLogActionEntry(d)
