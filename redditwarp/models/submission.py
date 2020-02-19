
from datetime import datetime, timezone
from ..util import AttributeCollection

class Submission:
	THING_PREFIX = 't3_'

	def __init__(self, data):
		self.a = AttributeCollection(self)
		self._update(data)
		self.b = data

	def _update(self, data):
		self.id = int(data['id'], 36)
		self.id36 = data['id']
		self.full_id36 = self.THING_PREFIX + data['id']
		self.created_at = datetime.fromtimestamp(data['created_utc'], timezone.utc)
		self.created_ut = int(data['created_utc'])

	def __repr__(self):
		return f'<{self.__class__.__name__} id36={self.id36!r}>'

class TextPost(Submission):
	def _update(self, data):
		super()._update(data)
		self.body = data['selftext']
		self.body_html = data['selftext_html']

class LinkPost(Submission):
	pass
