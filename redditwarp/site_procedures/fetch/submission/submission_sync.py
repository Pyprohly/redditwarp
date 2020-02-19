
from ....models.submission import LinkPost, TextPost

class submission:
	def __init__(self, client):
		self._client = client

	def __call__(self, full_id36):
		data = self._client.request('GET', '/api/info', params={'id': full_id36})
		children = data['data']['children']
		if not children:
			return None
		data = children[0]['data']
		if data['is_self']:
			return TextPost(data)
		return LinkPost(data)

	def textpost(self, full_id36):
		data = self._client.request('GET', '/api/info', params={'id': full_id36})
		children = data['data']['children']
		if not children:
			return None
		data = children[0]['data']
		if data['is_self']:
			return TextPost(data)
		return None

	def linkpost(self, full_id36):
		data = self._client.request('GET', '/api/info', params={'id': full_id36})
		children = data['data']['children']
		if not children:
			return None
		data = children[0]['data']
		if not data['is_self']:
			return LinkPost(data)
		return None

	def comments_composite(self):
		pass
