
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..live_thread_SYNC import LiveThread, LiveUpdate

def load_live_thread(d: Mapping[str, Any], client: Client) -> LiveThread:
    return LiveThread(d, client)

def load_live_update(d: Mapping[str, Any], client: Client) -> LiveUpdate:
    return LiveUpdate(d, client)
