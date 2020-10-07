
from __future__ import annotations
from typing import Any, Mapping

from ..util.data_members_namespace import DataMembersNamespaceMapping
from ..util.attribute_mapping_wrapper import PrettyPrintingAttributeMappingWrapper

class FunBox:
    """An object with fun interactive capabilities."""

    def __init__(self, d: Mapping[str, Any]):
        self.a = DataMembersNamespaceMapping(self)
        self.b = PrettyPrintingAttributeMappingWrapper(d)
