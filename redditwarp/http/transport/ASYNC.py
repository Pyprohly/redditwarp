
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Optional
if TYPE_CHECKING:
    from types import ModuleType
    from importlib.machinery import ModuleSpec
    from ..session_base_ASYNC import SessionBase

import sys
from importlib.util import find_spec

from ...util.imports import load_module_from_spec

def load_spec(name: str, package: Optional[str] = None) -> ModuleSpec:
    module_spec = find_spec(name, package)
    if module_spec is None:
        raise RuntimeError(f'module spec not found: {name} ({package})')
    return module_spec

def get_transport_module() -> ModuleType:
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
                raise ModuleNotFoundError('An HTTP transport library needs to be installed.')

        transport_registry[name] = module

    return module

def new_session(*,
    default_timeout: float = 8,
) -> SessionBase:
    module = get_transport_module()
    new_session = module.new_session  # type: ignore[attr-defined]
    return new_session(default_timeout=default_timeout)

def get_session_underlying_library_name_and_version(session: object) -> tuple[str, str]:
    module = sys.modules[session.__module__]

    conforming = getattr(module, 'STRUCTURAL_CONFORMITY', False)
    if not conforming:
        return ('', '')

    name = module.name  # type: ignore[attr-defined]
    version = module.version  # type: ignore[attr-defined]
    return (name, version)

transport_module_spec_registry: MutableMapping[str, ModuleSpec] = {
    'httpx': load_spec('.httpx_async', __package__),
    'aiohttp': load_spec('.aiohttp', __package__),
}
transport_registry: MutableMapping[str, ModuleType] = {}
