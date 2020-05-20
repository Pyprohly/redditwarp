
from __future__ import annotations
from typing import Any, Mapping

from ..util.data_members_namespace import AttributeCollection
from ..util.attributedict import AttributeDict

class Object:
	pass

class FancyAttributeNamespaces(Object):
	def __init__(self, d: MutableMapping[str, Any]):
		self.a = AttributeCollection(self)
		self.b = AttributeDict(d)
