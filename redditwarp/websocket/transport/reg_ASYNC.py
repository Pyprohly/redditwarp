
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Sequence, Protocol, MutableSequence
if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec

from dataclasses import dataclass

from ...util.imports import load_spec, import_module_from_spec
from ..websocket_ASYNC import WebSocket


class ConnectFunctionProtocol(Protocol):
    async def __call__(self, url: str, *,
        subprotocols: Sequence[str] = (), timeout: float = -2
    ) -> WebSocket: ...

@dataclass
class TransportInfo:
    adaptor_module_name: str
    name: str
    version: str
    connect: ConnectFunctionProtocol


def load_transport() -> TransportInfo:
    if not transport_info_registry:
        for module_spec in transport_module_spec_list:
            try:
                import_module_from_spec(module_spec)
            except ImportError:
                continue
            break
        else:
            raise ModuleNotFoundError('A websocket transport library needs to be installed.')

    return next(iter(transport_info_registry.values()))

async def connect(url: str, *,
        subprotocols: Sequence[str] = (), timeout: float = -2) -> WebSocket:
    connect = load_transport().connect
    return await connect(url, subprotocols=subprotocols, timeout=timeout)

def register(
    adaptor_module_name: str,
    name: str,
    version: str,
    connect: ConnectFunctionProtocol,
) -> None:
    info = TransportInfo(
        adaptor_module_name=adaptor_module_name,
        name=name,
        version=version,
        connect=connect,
    )
    transport_info_registry[adaptor_module_name] = info

transport_module_spec_list: MutableSequence[ModuleSpec] = [
    load_spec('.carriers.websockets', __package__),
    load_spec('.carriers.aiohttp', __package__),
]
transport_info_registry: MutableMapping[str, TransportInfo] = {}
