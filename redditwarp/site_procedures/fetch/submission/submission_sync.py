
from ....models.submission import LinkPost, TextPost
from ....util.base_conversion import to_base36

def _fetch_submission_data(client, full_id36):
	data = client.request('GET', '/api/info', params={'id': full_id36})
	children = data['data']['children']
	if not children:
		return None
	return children[0]['data']

class textpost():
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

	def __call__(self, id):
		return self.by_id36(to_base36(id))

	def by_id36(self, id36):
		data = _fetch_submission_data(self._client, 't3_' + id36)
		if data is None:
			return None
		if data['is_self']:
			return TextPost(data)
		return None

class linkpost():
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

	def __call__(self, id):
		return self.by_id36(to_base36(id))

	def by_id36(self, id36):
		data = _fetch_submission_data(self._client, 't3_' + id36)
		if data is None:
			return None
		if data['is_self']:
			return None
		return LinkPost(data)

class comments_composite():
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

class submission():
	def __init__(self, client):
		self._client = client
		self.textpost = textpost(self, client)
		self.linkpost = linkpost(self, client)
		self.comments_composite = comments_composite(self, client)

	def __call__(self, id):
		return self.by_id36(to_base36(id))

	def by_id36(self, id36):
		data = _fetch_submission_data(self._client, 't3_' + id36)
		if data is None:
			return None
		if data['is_self']:
			return TextPost(data)
		return LinkPost(data)
