
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Optional, Mapping, TypeVar, Callable, Sequence
if TYPE_CHECKING:
    from types import ModuleType
    from importlib.machinery import ModuleSpec
    from ..transporter_info import TransporterInfo

import importlib.util
from importlib.abc import Loader

T = TypeVar('T')

def load_module_from_spec(spec: ModuleSpec) -> Optional[ModuleType]:
    if spec.loader is None:
        raise RuntimeError('spec has no loader')
    assert isinstance(spec.loader, Loader)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    return module

def register_factory(
    transporter_info_registry: MutableMapping[str, TransporterInfo],
    transporter_session_function_registry: MutableMapping[str, T],
) -> Callable[[str, TransporterInfo, T], None]:
    def _f(name: str, info: TransporterInfo, new_session_func: T) -> None:
        transporter_info_registry[name] = info
        transporter_session_function_registry[name] = new_session_func
    return _f

def try_get_default_transporter_name_factory(
    priority: Sequence[str],
    info_registry: Mapping[str, TransporterInfo],
    module_spec_registry: Mapping[str, ModuleSpec],
) -> Callable[[], Optional[str]]:
    def _f() -> Optional[str]:
        for name in priority:
            if name in info_registry:
                return name

        for name in priority:
            spec = module_spec_registry[name]
            module = load_module_from_spec(spec)
            if module is None:
                continue

            if name not in info_registry:
                raise Exception('the transporter module did not register correctly')
            return name

        return None
    return _f

def get_default_transporter_name_factory(
    try_get_default_transporter_name: Callable[[], Optional[str]],
) -> Callable[[], str]:
    def _f() -> str:
        name = try_get_default_transporter_name()
        if name is None:
            raise ModuleNotFoundError('An HTTP transport library needs to be installed.')
        return name
    return _f

def new_session_factory_factory(
    transporter_session_function_registry: Mapping[str, T]
) -> Callable[[str], T]:
    def _f(transporter_name: str) -> T:
        return transporter_session_function_registry[transporter_name]
    return _f

def transporter_info_factory(
    transporter_info_registry: Mapping[str, T]
) -> Callable[[str], T]:
    def _f(transporter_name: str) -> T:
        return transporter_info_registry[transporter_name]
    return _f


m: MutableMapping[str, Optional[ModuleSpec]] = {
    'requests': importlib.util.find_spec('.requests', __package__),
    'aiohttp': importlib.util.find_spec('.aiohttp', __package__),
    'httpx_sync': importlib.util.find_spec('.httpx_sync', __package__),
    'httpx_async': importlib.util.find_spec('.httpx_async', __package__),
}
raw_transporter_module_spec_registry: MutableMapping[str, ModuleSpec] = {
    k: v for k, v in m.items() if v is not None
}
