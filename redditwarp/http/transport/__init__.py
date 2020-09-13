
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, MutableMapping, Callable
if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from ..base_session_sync import BaseSession as SyncBaseSession
    from ..base_session_async import BaseSession as AsyncBaseSession

import importlib.util
from importlib.abc import Loader
from types import ModuleType

from ._init_ import (  # noqa
    sync_transporter_info_registry,
    sync_transporter_session_function_registry,
    register_sync,
    async_transporter_info_registry,
    async_transporter_session_function_registry,
    register_async,
)

def load_module_from_spec(spec: ModuleSpec) -> Optional[ModuleType]:
    if spec.loader is None:
        raise Exception
    assert isinstance(spec.loader, Loader)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    return module


m: MutableMapping[str, Optional[ModuleSpec]] = {
    'requests': importlib.util.find_spec('.requests', __name__),
    'aiohttp': importlib.util.find_spec('.aiohttp', __name__),
    'httpx_sync': importlib.util.find_spec('.httpx_sync', __name__),
    'httpx_async': importlib.util.find_spec('.httpx_async', __name__),
}
raw_transporter_module_spec_registry: MutableMapping[str, ModuleSpec] = {k: v for k, v in m.items() if v is not None}

#region sync

sync_transporter_priority = ['httpx', 'requests']
sync_transporter_module_spec_registry = {
    'httpx': raw_transporter_module_spec_registry['httpx_sync'],
    'requests': raw_transporter_module_spec_registry['requests'],
}

def try_get_default_sync_transporter_name() -> Optional[str]:
    for name in sync_transporter_priority:
        if name in sync_transporter_info_registry:
            return name

    for name in sync_transporter_priority:
        spec = sync_transporter_module_spec_registry[name]
        module = load_module_from_spec(spec)
        if module is None:
            continue

        if name not in sync_transporter_info_registry:
            raise Exception('the transporter module did not register properly')

        return name

    return None

def get_default_sync_transporter_name() -> str:
    name = try_get_default_sync_transporter_name()
    if name is None:
        raise ModuleNotFoundError('An HTTP transport library needs to be installed.')
    return name

def new_sync_session_factory(transporter_name: str) -> Callable[..., SyncBaseSession]:
    return sync_transporter_session_function_registry[transporter_name]

#endregion

#region async

async_transporter_priority = ['httpx', 'aiohttp']
async_transporter_module_spec_registry = {
    'httpx': raw_transporter_module_spec_registry['httpx_async'],
    'aiohttp': raw_transporter_module_spec_registry['aiohttp'],
}

def try_get_default_async_transporter_name() -> Optional[str]:
    for name in async_transporter_priority:
        if name in async_transporter_info_registry:
            return name

    for name in async_transporter_priority:
        spec = async_transporter_module_spec_registry[name]
        module = load_module_from_spec(spec)
        if module is None:
            continue

        if name not in async_transporter_info_registry:
            raise Exception('the transporter module did not register properly')

        return name

    return None

def get_default_async_transporter_name() -> str:
    name = try_get_default_async_transporter_name()
    if name is None:
        raise ModuleNotFoundError('An async HTTP transport library needs to be installed.')
    return name

def new_async_session_factory(transporter_name: str) -> Callable[..., AsyncBaseSession]:
    return async_transporter_session_function_registry[transporter_name]

#endregion
