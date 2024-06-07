
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Union
if TYPE_CHECKING:
    from types import ModuleType

import sys

from ...util.imports import load_spec, import_module_from_spec


_transport_adapter_module_name_list: Sequence[str] = (
    'websocket',
)
_current_transport_adapter_module: Optional[ModuleType] = None


def _init_transport_adapter_module() -> ModuleType:
    for module_name in _transport_adapter_module_name_list:
        module_spec = load_spec('.impls.' + module_name, __package__)
        try:
            return import_module_from_spec(module_spec)
        except ImportError:
            pass
    raise ModuleNotFoundError("A websocket transport library needs to be installed.")

def get_transport_adapter_module() -> ModuleType:
    global _current_transport_adapter_module
    if _current_transport_adapter_module is None:
        _current_transport_adapter_module = _init_transport_adapter_module()
    return _current_transport_adapter_module

def set_transport_adapter_module(module: ModuleType) -> None:
    global _current_transport_adapter_module
    _current_transport_adapter_module = module


def get_transport_adapter_module_name_and_version(module: Union[str, ModuleType]) -> tuple[str, str]:
    m = module
    if isinstance(m, str):
        m = sys.modules[m]
    try:
        return (m.name, m.version)
    except AttributeError as e:
        raise RuntimeError from e
