
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Optional, Protocol
if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from ..session_base_SYNC import SessionBase

from importlib.util import find_spec
from dataclasses import dataclass

from ...util.imports import load_module_from_spec

class NewSessionFunction(Protocol):
    def __call__(self, *,
        default_timeout: float = 8,
    ) -> SessionBase:
        pass

@dataclass
class TransportInfo:
    adaptor_module_name: str
    new_session: NewSessionFunction
    name: str
    version: str

def load_spec(name: str, package: Optional[str] = None) -> ModuleSpec:
    module_spec = find_spec(name, package)
    if module_spec is None:
        raise RuntimeError(f'module spec not found: {name} ({package})')
    return module_spec

def load_transport() -> TransportInfo:
    if not transport_info_registry:
        for module_spec in transport_module_spec_list:
            try:
                load_module_from_spec(module_spec)
            except ImportError:
                continue
            break
        else:
            raise ModuleNotFoundError('An HTTP transport library needs to be installed.')

    return next(iter(transport_info_registry.values()))

def new_session(*,
    default_timeout: float = 8,
) -> SessionBase:
    new_session = load_transport().new_session
    return new_session(default_timeout=default_timeout)

def register(
    adaptor_module_name: str,
    new_session: NewSessionFunction,
    name: str,
    version: str,
) -> None:
    info = TransportInfo(
        adaptor_module_name,
        new_session,
        name,
        version,
    )
    transport_info_registry[adaptor_module_name] = info

transport_module_spec_list = [
    load_spec('.httpx_sync', __package__),
    load_spec('.requests', __package__),
]
transport_info_registry: MutableMapping[str, TransportInfo] = {}
