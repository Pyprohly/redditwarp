
from ..util.data_members_namespace import AttributeCollection
from ..util.attributedict import AttributeDict

class Object:
	pass

class FancyAttributeNamespaces(Object):
	BASE_ATTR_DEPS = {}

	def __init__(self, data):
		self.a = AttributeCollection(self)
		self.b = AttributeDict(data)
