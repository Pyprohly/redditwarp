
from __future__ import annotations
from typing import TYPE_CHECKING, MutableMapping, Optional, Mapping, Protocol
if TYPE_CHECKING:
    from ..transporter_info import TransporterInfo
    from ..base_session_SYNC import BaseSession

from . import (
    raw_transporter_module_spec_registry,
    register_factory,
    try_get_default_transporter_name_factory,
    get_default_transporter_name_factory,
    new_session_factory_factory,
    transporter_info_factory,
)

class NewSessionFunction(Protocol):
    def __call__(self, *,
        params: Optional[Mapping[str, Optional[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> BaseSession:
        pass

transporter_info_registry: MutableMapping[str, TransporterInfo] = {}
transporter_session_function_registry: MutableMapping[str, NewSessionFunction] = {}

register = register_factory(
    transporter_info_registry,
    transporter_session_function_registry,
)

transporter_priority = ['httpx', 'requests']
transporter_module_spec_registry = {
    'httpx': raw_transporter_module_spec_registry['httpx_SYNC'],
    'requests': raw_transporter_module_spec_registry['requests'],
}

try_get_default_transporter_name = try_get_default_transporter_name_factory(
    transporter_priority,
    transporter_info_registry,
    transporter_module_spec_registry,
)
get_default_transporter_name = get_default_transporter_name_factory(
    try_get_default_transporter_name,
)
new_session_factory = new_session_factory_factory(
    transporter_session_function_registry,
)
transporter_info = transporter_info_factory(
    transporter_info_registry,
)
