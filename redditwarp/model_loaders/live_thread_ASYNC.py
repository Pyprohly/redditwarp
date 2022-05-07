
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from ..models.live_thread_ASYNC import LiveThread, LiveUpdate

def load_live_thread(d: Mapping[str, Any], client: Client) -> LiveThread:
    return LiveThread(d, client)

def load_live_update(d: Mapping[str, Any], client: Client) -> LiveUpdate:
    return LiveUpdate(d, client)
