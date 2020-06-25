
from typing import MutableMapping, Optional
from ..transporter_info import TransporterInfo

from contextlib import suppress

#region sync

sync_transporter_priority = ['requests']
sync_transporter_registry: MutableMapping[str, Optional[TransporterInfo]] = {}

def get_default_sync_transporter() -> Optional[TransporterInfo]:
    info: Optional[TransporterInfo] = None
    with suppress(ImportError):
        from .requests import info  # type: ignore[no-redef]
    sync_transporter_registry['requests'] = info

    for u in sync_transporter_priority:
        t = sync_transporter_registry[u]
        if t is not None:
            break
    return t

#endregion

#region async

async_transporter_priority = ['aiohttp']
async_transporter_registry: MutableMapping[str, Optional[TransporterInfo]] = {}

def get_default_async_transporter() -> Optional[TransporterInfo]:
    info: Optional[TransporterInfo] = None
    with suppress(ImportError):
        from .aiohttp import info  # type: ignore[no-redef]
    async_transporter_registry['aiohttp'] = info

    for u in async_transporter_priority:
        t = async_transporter_registry[u]
        if t is not None:
            break
    return t

#endregion
