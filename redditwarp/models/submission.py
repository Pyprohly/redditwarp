
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


class fetch_submission:
	def __init__(self, client):
		self.client = client

	def __call__(self, full_id36):
		data = self.client.request('GET', '/api/info', params={'id': full_id36})
		children = data['data']['children']
		if not children:
			return None
		data = children[0]['data']
		if data['is_self']:
			return TextPost(data)
		return LinkPost(data)

	def textpost(self, full_id36):
		data = self.client.request('GET', '/api/info', params={'id': full_id36})
		children = data['data']['children']
		if not children:
			return None
		data = children[0]['data']
		if data['is_self']:
			return TextPost(data)
		return None

	def linkpost(self, full_id36):
		data = self.client.request('GET', '/api/info', params={'id': full_id36})
		children = data['data']['children']
		if not children:
			return None
		data = children[0]['data']
		if not data['is_self']:
			return LinkPost(data)
		return None

	def comments_composite(self):
		pass
