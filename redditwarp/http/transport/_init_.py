
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Optional, Mapping, Protocol
if TYPE_CHECKING:
    from ..transporter_info import TransporterInfo
    from ..base_session_sync import BaseSession as SyncBaseSession
    from ..base_session_async import BaseSession as AsyncBaseSession

class NewSyncSessionFunction(Protocol):
    def __call__(self, *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> SyncBaseSession:
        pass

class NewAsyncSessionFunction(Protocol):
    def __call__(self, *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> AsyncBaseSession:
        pass

#region sync

sync_transporter_info_registry: MutableMapping[str, TransporterInfo] = {}
sync_transporter_session_function_registry: MutableMapping[str, NewSyncSessionFunction] = {}

def register_sync(name: str, info: TransporterInfo, new_session: NewSyncSessionFunction) -> None:
    sync_transporter_info_registry[name] = info
    sync_transporter_session_function_registry[name] = new_session

#endregion

#region async

async_transporter_info_registry: MutableMapping[str, TransporterInfo] = {}
async_transporter_session_function_registry: MutableMapping[str, NewAsyncSessionFunction] = {}

def register_async(name: str, info: TransporterInfo, new_session: NewAsyncSessionFunction) -> None:
    async_transporter_info_registry[name] = info
    async_transporter_session_function_registry[name] = new_session

#endregion
