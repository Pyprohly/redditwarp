
from __future__ import annotations
from typing import Any, MutableMapping

from ..util.data_members_namespace import AttributeCollection
from ..util.attribute_mapping_wrapper import AttributeMappingWrapper

class FunBox:
	def __init__(self, d: MutableMapping[str, Any]):
		self.a = AttributeCollection(self)
		self.b = AttributeMappingWrapper(d)
