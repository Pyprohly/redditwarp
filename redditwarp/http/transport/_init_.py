
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Callable
if TYPE_CHECKING:
    from ..transporter_info import TransporterInfo
    from ..base_session_sync import BaseSession as SyncBaseSession
    from ..base_session_async import BaseSession as AsyncBaseSession

#region sync

sync_transporter_info_registry: MutableMapping[str, TransporterInfo] = {}
sync_transporter_session_function_registry: MutableMapping[str, Callable[..., SyncBaseSession]] = {}

def register_sync(name: str, info: TransporterInfo, new_session: Callable[..., SyncBaseSession]) -> None:
    sync_transporter_info_registry[name] = info
    sync_transporter_session_function_registry[name] = new_session

#endregion

#region async

async_transporter_info_registry: MutableMapping[str, TransporterInfo] = {}
async_transporter_session_function_registry: MutableMapping[str, Callable[..., AsyncBaseSession]] = {}

def register_async(name: str, info: TransporterInfo, new_session: Callable[..., AsyncBaseSession]) -> None:
    async_transporter_info_registry[name] = info
    async_transporter_session_function_registry[name] = new_session

#endregion
