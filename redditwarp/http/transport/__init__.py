
from typing import MutableMapping, Optional, cast
from ..transporter_info import TransporterInfo

from contextlib import suppress

#region sync

sync_transporters = ['requests']
sync_transporter_registry: MutableMapping[str, Optional[TransporterInfo]] = {}

info: Optional[TransporterInfo] = None
with suppress(ImportError):
    from .requests import info
sync_transporter_registry['requests'] = info

default_sync_transporter: TransporterInfo = \
        cast(TransporterInfo, sync_transporter_registry['requests'])

#endregion

#region async

async_transporters = ['aiohttp']
async_transporter_registry: MutableMapping[str, Optional[TransporterInfo]] = {}

info = None
with suppress(ImportError):
    from .requests import info
async_transporter_registry['aiohttp'] = info

default_async_transporter: TransporterInfo = \
        cast(TransporterInfo, async_transporter_registry['aiohttp'])

#endregion
