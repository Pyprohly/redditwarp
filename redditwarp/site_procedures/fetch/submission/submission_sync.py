
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, TypeVar
if TYPE_CHECKING:
	from ....client_sync import Client
	from ....models.submission import Submission

from ....models.submission import LinkPost, TextPost
from ....util.base_conversion import to_base36

T = TypeVar('T')

def _by_id(
	id: int,
	by_id36: Callable[[str], Optional[T]],
) -> Optional[T]:
	id36 = to_base36(id)
	return by_id36(id36)

def _by_id36(
	client: Client,
	id36: str,
	parse_for_submission: Callable[[Mapping[str, Any]], Optional[T]],
) -> Optional[T]:
	t_id36 = 't3_' + id36
	res_data = client.request('GET', '/api/info', params={'id': t_id36})
	return parse_for_submission(res_data)


class as_textpost:
	def __init__(self, client: Client):
		self._client = client

	def __call__(self, id: int) -> Optional[TextPost]:
		return _by_id(id, self.by_id36)

	def by_id36(self, id36: str) -> Optional[TextPost]:
		def parse_for_submission(root: Mapping[str, Any]) -> Optional[TextPost]:
			children = root['data']['children']
			if not children:
				return None
			data = children[0]['data']
			is_textpost = data['is_self']
			if is_textpost:
				return TextPost(data)
			return None

		return _by_id36(self._client, id36, parse_for_submission)

class as_linkpost:
	def __init__(self, client: Client):
		self._client = client

	def __call__(self, id: int) -> Optional[LinkPost]:
		return _by_id(id, self.by_id36)

	def by_id36(self, id36: str) -> Optional[LinkPost]:
		def parse_for_submission(root: Mapping[str, Any]) -> Optional[LinkPost]:
			children = root['data']['children']
			if not children:
				return None
			data = children[0]['data']
			is_textpost = data['is_self']
			if not is_textpost:
				return LinkPost(data)
			return None

		return _by_id36(self._client, id36, parse_for_submission)

class comments_composite:
	def __init__(self, client: Client):
		self._client = client

class submission:
	def __init__(self, client: Client):
		self._client = client
		self.as_textpost = as_textpost(client)
		self.as_linkpost = as_linkpost(client)
		self.comments_composite = comments_composite(client)

	def __call__(self, id: int) -> Optional[Submission]:
		return _by_id(id, self.by_id36)

	def by_id36(self, id36: str) -> Optional[Submission]:
		def parse_for_submission(root: Mapping[str, Any]) -> Optional[Submission]:
			children = root['data']['children']
			if not children:
				return None
			data = children[0]['data']
			is_textpost = data['is_self']
			return TextPost(data) if is_textpost else LinkPost(data)

		return _by_id36(self._client, id36, parse_for_submission)
