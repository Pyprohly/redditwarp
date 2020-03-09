
from __future__ import annotations

from functools import partial

from ....models.submission import LinkPost, TextPost
from ....util.base_conversion import to_base36
from ....util.chunked import chunked
from ....util.the_stubborn_caller_iterator import TheStubbornCallerIterator
from ....util.obstinate_chain_iterator import ObstinateChainIterator

class as_textposts:
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

	def __call__(self, id):
		_check_id(id)
		id36 = to_base36(id)
		return _fetch_textpost_by_id36(client, id36)

	def by_id36(self, id36):
		_check_id36(id36)
		return _fetch_textpost_by_id36(client, id36)

class as_linkposts:
	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

	def __call__(self, id):
		_check_id(id)
		id36 = to_base36(id)
		return _fetch_linkpost_by_id36(client, id36)

	def by_id36(self, id36):
		_check_id36(id36)
		return _fetch_linkpost_by_id36(client, id36)


class via_call_chunks:
	@staticmethod
	def _api_info_call_chunk(client, id_str):
		def __():
			root = client.request('GET', '/api/info', params={'id': id_str})
			children = root['data']['children']
			output = []
			append = output.append
			for child in children:
				data = child['data']
				is_textpost = data['is_self']
				cls = TextPost if is_textpost else LinkPost
				append(cls(data))
			return output
		return __

	@staticmethod
	def _api_info_call_chunks(client, it):
		for seq in chunked(it, 100):
			p = ','.join(seq)
			yield _api_info_call_chunk(client, p)

	def __init__(self, outer, client):
		self._outer = outer
		self._client = client

	def __call__(self, ids):
		"""
		Parameters
		----------
		ids: Iterable[int]

		Returns
		-------
		Callable[[], Collection[Submission]]
		"""
		it = ('t3_' + to_base36(i) for i in ids if i >= 0)
		yield from self._api_info_call_chunks(self._client, it)

	def by_id36(self, id36s):
		"""
		Parameters
		----------
		id36s: Iterable[str]

		Returns
		-------
		Callable[[], Collection[Submission]]
		"""
		it = ('t3_' + i for i in id36s if i.isalnum())
		yield from self._api_info_call_chunks(self._client, it)

class submissions:
	def __init__(self, client):
		self._client = client
		self.via_call_chunks = via_call_chunks(self, client)
		self.as_textposts = as_textposts(self, client)
		self.as_linkposts = as_linkposts(self, client)

	def __call__(self, ids):
		"""
		Parameters
		----------
		ids: Iterable[int]

		Returns
		-------
		Iterator[Submission]
		"""
		return ObstinateChainIterator(TheStubbornCallerIterator(self.via_call_chunks(ids)))

	def by_id36(self, id36s):
		"""
		Parameters
		----------
		id36s: Iterable[str]

		Returns
		-------
		Iterator[Submission]
		"""
		return ObstinateChainIterator(TheStubbornCallerIterator(self.via_call_chunks.by_id36(id36s)))
