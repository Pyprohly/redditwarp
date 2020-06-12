
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Dict, Any, List, Callable, Mapping, TypeVar
if TYPE_CHECKING:
	from ....client_sync import Client
	from ....models.submission import Submission

from ....models.submission import LinkPost, TextPost
from ....util.base_conversion import to_base36
from ....util.chunked import chunked
from ....util.call_chunk_chaining_iterator import CallChunkChainingIterator

T = TypeVar('T')

def _by_ids(
	ids: Iterable[int],
	by_id36s: Callable[[Iterable[str]], CallChunkChainingIterator[T]],
) -> CallChunkChainingIterator[T]:
	id36s = map(to_base36, ids)
	return by_id36s(id36s)

def _by_id36s(
	client: Client,
	id36s: Iterable[str],
	parse_for_submissions: Callable[[Mapping[str, Any]], List[T]],
) -> CallChunkChainingIterator[T]:
	t_id36s = map('t3_'.__add__, id36s)
	chunks = chunked(t_id36s, 100)
	strseqs = map(','.join, chunks)

	def api_call_func(ids_str: str, client: Client) -> Dict[str, Any]:
		return client.request('GET', '/api/info', params={'id': ids_str})

	def call_chunk(ids_str: str, client: Client = client) -> Callable[[], List[T]]:
		return lambda: parse_for_submissions(api_call_func(ids_str, client))

	call_chunks = map(call_chunk, strseqs)
	return CallChunkChainingIterator(call_chunks)


class as_textposts:
	def __init__(self, client: Client):
		self._client = client

	def __call__(self, ids: Iterable[int]) -> CallChunkChainingIterator[TextPost]:
		return _by_ids(ids, self.by_id36s)

	def by_id36s(self, id36s: Iterable[str]) -> CallChunkChainingIterator[TextPost]:
		def parse_for_submissions(root: Mapping[str, Any]) -> List[TextPost]:
			submissions_data = (child['data'] for child in root['data']['children'])
			output = []
			for data in submissions_data:
				is_textpost = data['is_self']
				if is_textpost:
					output.append(TextPost(data))
			return output

		return _by_id36s(self._client, id36s, parse_for_submissions)

class as_linkposts:
	def __init__(self, client: Client):
		self._client = client

	def __call__(self, ids: Iterable[int]) -> CallChunkChainingIterator[LinkPost]:
		return _by_ids(ids, self.by_id36s)

	def by_id36s(self, id36s: Iterable[str]) -> CallChunkChainingIterator[LinkPost]:
		def parse_for_submissions(root: Mapping[str, Any]) -> List[LinkPost]:
			submissions_data = (child['data'] for child in root['data']['children'])
			output = []
			for data in submissions_data:
				is_textpost = data['is_self']
				if not is_textpost:
					output.append(LinkPost(data))
			return output

		return _by_id36s(self._client, id36s, parse_for_submissions)

class submissions:
	def __init__(self, client: Client):
		self._client = client
		self.as_textposts = as_textposts(client)
		self.as_linkposts = as_linkposts(client)

	def __call__(self, ids: Iterable[int]) -> CallChunkChainingIterator[Submission]:
		return _by_ids(ids, self.by_id36s)

	def by_id36s(self, id36s: Iterable[str]) -> CallChunkChainingIterator[Submission]:
		def parse_for_submissions(root: Mapping[str, Any]) -> List[Submission]:
			submissions_data = (child['data'] for child in root['data']['children'])
			output = []
			for data in submissions_data:
				is_textpost = data['is_self']
				klass = TextPost if is_textpost else LinkPost
				output.append(klass(data))
			return output

		return _by_id36s(self._client, id36s, parse_for_submissions)
