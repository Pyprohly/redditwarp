
from __future__ import annotations
from typing import Any, Mapping

from ..util.data_members_namespace import AttributeCollection
from ..util.attribute_mapping_wrapper import AttributeMappingWrapper

class FunBox:
    """An object with fun interactive capabilities."""

    def __init__(self, d: Mapping[str, Any]):
        self.a = AttributeCollection(self)
        self.b = AttributeMappingWrapper(d)
