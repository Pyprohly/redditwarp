
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Protocol, MutableSequence
if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from .connector_ASYNC import Connector

from dataclasses import dataclass

from ...util.imports import load_spec, import_module_from_spec


class NewConnectorFunctionProtocol(Protocol):
    def __call__(self) -> Connector: ...

@dataclass
class TransportInfo:
    adaptor_module_name: str
    name: str
    version: str
    new_connector: NewConnectorFunctionProtocol


def load_transport() -> TransportInfo:
    if not transport_registry:
        for module_spec in transport_module_spec_list:
            try:
                import_module_from_spec(module_spec)
            except ImportError:
                continue
            break
        else:
            raise ModuleNotFoundError('An HTTP transport library needs to be installed.')

    return next(iter(transport_registry.values()))

def new_connector() -> Connector:
    new_connector = load_transport().new_connector
    return new_connector()

def register(
    *,
    adaptor_module_name: str,
    name: str,
    version: str,
    new_connector: NewConnectorFunctionProtocol,
) -> None:
    info = TransportInfo(
        adaptor_module_name=adaptor_module_name,
        name=name,
        version=version,
        new_connector=new_connector,
    )
    transport_registry[adaptor_module_name] = info

transport_module_spec_list: MutableSequence[ModuleSpec] = [
    load_spec('.connectors.httpx_async', __package__),
    load_spec('.connectors.aiohttp', __package__),
]
transport_registry: MutableMapping[str, TransportInfo] = {}
