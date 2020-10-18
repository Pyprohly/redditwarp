
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Any, List, Callable, Mapping
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.subreddit_SYNC import Subreddit

from ...load.subreddit_SYNC import load_subreddit
from ....util.base_conversion import to_base36
from ....iterators.chunking_iterator import ChunkingIterator
from ....iterators.call_chunk_chaining_iterator import ChunkSizeAdjustableCallChunkChainingIterator

class BulkFetch:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[Subreddit]:
        return self.by_id(ids)

    def _load_object(self, m: Mapping[str, Any]) -> Subreddit:
        return load_subreddit(m, self._client)

    def by_id(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[Subreddit]:
        id36s = map(to_base36, ids)
        return self.by_id36(id36s)

    def by_id36(self, id36s: Iterable[str]) -> ChunkSizeAdjustableCallChunkChainingIterator[Subreddit]:
        full_id36s = map('t5_'.__add__, id36s)
        chunk_iter = ChunkingIterator(full_id36s, 100)
        strseqs = map(','.join, chunk_iter)

        def call_chunk(ids_str: str) -> Callable[[], List[Subreddit]]:
            def f() -> List[Subreddit]:
                root = self._client.request('GET', '/api/info', params={'id': ids_str})
                data = root['data']
                return list(map(self._load_object, data['children']))
            return f

        call_chunks = map(call_chunk, strseqs)
        return ChunkSizeAdjustableCallChunkChainingIterator(call_chunks, chunk_iter)
