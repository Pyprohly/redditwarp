
from datetime import datetime, timezone
from .object import FancyAttributeNamespaces
from .design_classes import ThingMixin

class Submission(ThingMixin, FancyAttributeNamespaces):
	THING_PREFIX = 't3'

	BASE_ATTR_DEPS = {
		'id': ('id',),
		'id36': ('id',),
		'full_id36': ('id',),
		'created_at': ('created_utc',),
		'created_ut': ('created_utc',),
	}

	def __init__(self, data):
		super().__init__(data)
		self.__set_attrs(data)

	def __set_attrs(self, data):
		self.created_at = datetime.fromtimestamp(data['created_utc'], timezone.utc)
		self.created_ut = int(data['created_utc'])

class TextPost(Submission):
	def __init__(self, data):
		super().__init__(data)
		self.body = data['selftext']
		self.body_html = data['selftext_html']

class LinkPost(Submission):
	pass
