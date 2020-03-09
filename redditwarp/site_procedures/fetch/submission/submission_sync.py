
from __future__ import annotations

from ....models.submission import LinkPost, TextPost
from ....util.base_conversion import to_base36

def _check_id(v):
	if v < 0:
		raise ValueError('negative ID not allowed')

def _check_id36(v):
	if not v.isalnum():
		raise ValueError('value must be alpha-numeric')

def _fetch_data(client, full_id36):
	data = client.request('GET', '/api/info', params={'id': full_id36})
	children = data['data']['children']
	if not children:
		return None
	return children[0]['data']

def _fetch_submission_by_id36(client, id36):
	data = _fetch_data(client, 't3_' + id36)
	if data is None:
		return None
	if data['is_self']:
		return TextPost(data)
	return LinkPost(data)

def _fetch_textpost_by_id36(client, id36):
	data = _fetch_data(client, 't3_' + id36)
	if data is None:
		return None
	if data['is_self']:
		return TextPost(data)
	return None

def _fetch_linkpost_by_id36(client, id36):
	data = _fetch_data(client, 't3_' + id36)
	if data is None:
		return None
	if data['is_self']:
		return None
	return LinkPost(data)

class as_textpost:
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

	def __call__(self, id: int) -> TextPost:
		_check_id(id)
		id36 = to_base36(id)
		return _fetch_textpost_by_id36(self._client, id36)

	def by_id36(self, id36: str) -> TextPost:
		_check_id36(id36)
		return _fetch_textpost_by_id36(self._client, id36)

class as_linkpost:
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

	def __call__(self, id: int) -> LinkPost:
		_check_id(id)
		id36 = to_base36(id)
		return _fetch_linkpost_by_id36(self._client, id36)

	def by_id36(self, id36: str) -> LinkPost:
		_check_id36(id36)
		return _fetch_linkpost_by_id36(self._client, id36)

class comments_composite:
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

class submission:
	def __init__(self, client):
		self._client = client
		self.as_textpost = as_textpost(self, client)
		self.as_linkpost = as_linkpost(self, client)
		self.comments_composite = comments_composite(self, client)

	def __call__(self, id: int) -> Submission:
		_check_id(id)
		id36 = to_base36(id)
		return _fetch_submission_by_id36(self._client, id36)

	def by_id36(self, id36: str) -> Submission:
		_check_id36(id36)
		return _fetch_submission_by_id36(self._client, id36)
