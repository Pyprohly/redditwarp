
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Dict, Any, List, Callable, Mapping, TypeVar
if TYPE_CHECKING:
    from ....client_sync import Client
    from ....models.submission import Submission

from ...load.submission import load_submission, try_load_linkpost, try_load_textpost
from ....models.submission import LinkPost, TextPost
from ....util.base_conversion import to_base36
from ....iterators.chunking_iterator import ChunkingIterator
from ....iterators.call_chunk_chaining_iterator import ChunkSizeAdjustableCallChunkChainingIterator

T = TypeVar('T')

def _by_ids(
    ids: Iterable[int],
    by_id36s: Callable[[Iterable[str]], ChunkSizeAdjustableCallChunkChainingIterator[T]],
) -> ChunkSizeAdjustableCallChunkChainingIterator[T]:
    id36s = map(to_base36, ids)
    return by_id36s(id36s)

def _by_id36s(
    client: Client,
    id36s: Iterable[str],
    parse_for_submissions: Callable[[Mapping[str, Any]], List[T]],
) -> ChunkSizeAdjustableCallChunkChainingIterator[T]:
    t_id36s = map('t3_'.__add__, id36s)
    chunk_iter = ChunkingIterator(t_id36s, 100)
    strseqs = map(','.join, chunk_iter)

    def api_call_func(ids_str: str, client: Client) -> Dict[str, Any]:
        return client.request('GET', '/api/info', params={'id': ids_str})

    def call_chunk(ids_str: str, client: Client = client) -> Callable[[], List[T]]:
        def f() -> List[T]:
            return parse_for_submissions(api_call_func(ids_str, client))
        return f
        #return lambda: parse_for_submissions(api_call_func(ids_str, client))

    call_chunks: Iterable[Callable[[], Iterable[T]]] = map(call_chunk, strseqs)
    return ChunkSizeAdjustableCallChunkChainingIterator(call_chunks, chunk_iter)


class as_textposts:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[TextPost]:
        return _by_ids(ids, self.by_id36s)

    def by_id36s(self, id36s: Iterable[str]) -> ChunkSizeAdjustableCallChunkChainingIterator[TextPost]:
        def parse_for_submissions(root: Mapping[str, Any]) -> List[TextPost]:
            data = root['data']
            return [
                m for m in
                (try_load_textpost(d) for d in data['children'])
                if m is not None
            ]

        return _by_id36s(self._client, id36s, parse_for_submissions)

class as_linkposts:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[LinkPost]:
        return _by_ids(ids, self.by_id36s)

    def by_id36s(self, id36s: Iterable[str]) -> ChunkSizeAdjustableCallChunkChainingIterator[LinkPost]:
        def parse_for_submissions(root: Mapping[str, Any]) -> List[LinkPost]:
            data = root['data']
            return [
                m for m in
                (try_load_linkpost(d) for d in data['children'])
                if m is not None
            ]

        return _by_id36s(self._client, id36s, parse_for_submissions)

class bulk_fetch:
    def __init__(self, client: Client):
        self._client = client
        self.as_textposts = as_textposts(client)
        self.as_linkposts = as_linkposts(client)

    def __call__(self, ids: Iterable[int]) -> ChunkSizeAdjustableCallChunkChainingIterator[Submission]:
        return _by_ids(ids, self.by_id36s)

    def by_id36s(self, id36s: Iterable[str]) -> ChunkSizeAdjustableCallChunkChainingIterator[Submission]:
        def parse_for_submissions(root: Mapping[str, Any]) -> List[Submission]:
            data = root['data']
            return [
                m for m in
                (load_submission(d) for d in data['children'])
                if m is not None
            ]

        return _by_id36s(self._client, id36s, parse_for_submissions)
