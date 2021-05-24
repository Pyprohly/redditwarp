
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Optional, Sequence
if TYPE_CHECKING:
    from types import ModuleType
    from importlib.machinery import ModuleSpec

import sys
from importlib.util import find_spec

from ...util.imports import load_module_from_spec
from ..websocket_connection_ASYNC import WebSocketConnection

def load_spec(name: str, package: Optional[str] = None) -> ModuleSpec:
    module_spec = find_spec(name, package)
    if module_spec is None:
        raise RuntimeError(f'module spec not found: {name} ({package})')
    return module_spec

def load_transport_module() -> ModuleType:
    itr = iter(transport_registry.items())
    try:
        name, module = next(itr)
    except StopIteration:
        for name, module_spec in transport_module_spec_registry.items():
            if name in sys.modules:
                module = load_module_from_spec(module_spec)
                break

        else:
            for name, module_spec in transport_module_spec_registry.items():
                try:
                    module = load_module_from_spec(module_spec)
                except ImportError:
                    continue
                break
            else:
                raise ModuleNotFoundError('A websocket transport library needs to be installed.')

        transport_registry[name] = module

    return module

async def connect(url: str, *,
        subprotocols: Sequence[str] = (), timeout: float = -2) -> WebSocketConnection:
    module = load_transport_module()
    connect = module.connect  # type: ignore[attr-defined]
    return await connect(url, subprotocols=subprotocols, timeout=timeout)

transport_module_spec_registry: MutableMapping[str, ModuleSpec] = {
    'websockets': load_spec('.websockets', __package__),
    'aiohttp': load_spec('.aiohttp', __package__),
}
transport_registry: MutableMapping[str, ModuleType] = {}
