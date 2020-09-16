
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Any, List, Callable, Mapping, TypeVar, Optional, Generic
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.submission import Submission

from ...load.submission import load_submission, try_load_linkpost, try_load_textpost
from ....models.submission import LinkPost, TextPost
from ....util.base_conversion import to_base36
from ....iterators.chunking_iterator import ChunkingIterator
from ....iterators.call_chunk_chaining_iterator import ChunkSizeAdjustableCallChunkChainingIterator

T = TypeVar('T')

class _common(Generic[T]):
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[T]:
        id36s = map(to_base36, ids)
        return self.by_id36s(id36s)

    def by_id36s(self, id36s: Iterable[str]) -> ChunkSizeAdjustableCallChunkChainingIterator[T]:
        t_id36s = map('t3_'.__add__, id36s)
        chunk_iter = ChunkingIterator(t_id36s, 100)
        strseqs = map(','.join, chunk_iter)

        def call_chunk(ids_str: str) -> Callable[[], List[T]]:
            def f() -> List[T]:
                root = self._client.request('GET', '/api/info', params={'id': ids_str})
                data = root['data']
                return [
                    m for m in
                    (self._load_object(d) for d in data['children'])
                    if m is not None
                ]
            return f

        call_chunks = map(call_chunk, strseqs)
        return ChunkSizeAdjustableCallChunkChainingIterator(call_chunks, chunk_iter)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[T]:
        raise NotImplementedError


class as_linkposts(_common[LinkPost]):
    def _load_object(self, m: Mapping[str, Any]) -> Optional[LinkPost]:
        return try_load_linkpost(m)

class as_textposts(_common[TextPost]):
    def _load_object(self, m: Mapping[str, Any]) -> Optional[TextPost]:
        return try_load_textpost(m)

class bulk_fetch(_common[Submission]):
    def __init__(self, client: Client):
        super().__init__(client)
        self.as_textposts = as_textposts(client)
        self.as_linkposts = as_linkposts(client)

    def _load_object(self, m: Mapping[str, Any]) -> Optional[Submission]:
        return load_submission(m)
