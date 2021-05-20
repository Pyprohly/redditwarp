
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Callable, List
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...models.load.partial_user import load_partial_user
from ...models.partial_user import PartialUser
from ...util.base_conversion import to_base36
from ...iterators.chunking_iterator import ChunkingIterator
from ...iterators.call_chunk_chaining_iterator import ChunkSizeAdjustableCallChunkChainingIterator
from ... import exceptions

class BulkFetchPartial:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[PartialUser]:
        return self.by_id(ids)

    def by_id(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[PartialUser]:
        id36s = map(to_base36, ids)
        return self.by_id36(id36s)

    def by_id36(self, id36s: Iterable[str]) -> ChunkSizeAdjustableCallChunkChainingIterator[PartialUser]:
        full_id36s = map('t2_'.__add__, id36s)
        chunk_iter = ChunkingIterator(full_id36s, 500)
        strseqs = map(','.join, chunk_iter)

        def call_chunk(ids_str: str) -> Callable[[], List[PartialUser]]:
            def f() -> List[PartialUser]:
                try:
                    root = self._client.request('GET', '/api/user_data_by_account_ids',
                            params={'ids': ids_str})
                except exceptions.HTTPStatusError as e:
                    if e.response.status == 404:
                        return []
                    raise

                return [load_partial_user(v, k) for k, v in root.items()]
            return f

        call_chunks = map(call_chunk, strseqs)
        return ChunkSizeAdjustableCallChunkChainingIterator(call_chunks, chunk_iter)
