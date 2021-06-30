
from __future__ import annotations
from typing import Any, Mapping

from ..live_thread import LiveThread, LiveThreadUpdate

def load_live_thread(d: Mapping[str, Any]) -> LiveThread:
    return LiveThread(d)

def load_live_thread_update(d: Mapping[str, Any]) -> LiveThreadUpdate:
    return LiveThreadUpdate(d)
