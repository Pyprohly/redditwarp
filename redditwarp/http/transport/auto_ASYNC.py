
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..connector_ASYNC import Connector

from .reg_ASYNC import get_transport_adapter_module


def new_connector() -> Connector:
    return get_transport_adapter_module().new_connector()
