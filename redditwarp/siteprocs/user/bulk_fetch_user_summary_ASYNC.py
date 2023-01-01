
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ...models.user_summary import UserSummary
from ...model_loaders.user_summary import load_user_summary
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ... import http

class BulkFetchUserSummary:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, ids: Iterable[int]) -> CallChunkChainingAsyncIterator[UserSummary]:
        async def mass_fetch_by_id(ids: Sequence[int]) -> Sequence[UserSummary]:
            id36s = map(to_base36, ids)
            full_id36s = map('t2_'.__add__, id36s)
            ids_str = ','.join(full_id36s)

            try:
                root = await self._client.request('GET', '/api/user_data_by_account_ids', params={'ids': ids_str})
            except http.exceptions.StatusCodeException as e:
                if e.status_code == 404:
                    return []
                raise
            return [load_user_summary(v, k) for k, v in root.items()]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch_by_id, idfs) for idfs in chunked(ids, 100))

    def by_id36(self, id36s: Iterable[str]) -> CallChunkChainingAsyncIterator[UserSummary]:
        async def mass_fetch_by_id36(id36s: Sequence[str]) -> Sequence[UserSummary]:
            full_id36s = map('t2_'.__add__, id36s)
            ids_str = ','.join(full_id36s)

            try:
                root = await self._client.request('GET', '/api/user_data_by_account_ids', params={'ids': ids_str})
            except http.exceptions.StatusCodeException as e:
                if e.status_code == 404:
                    return []
                raise
            return [load_user_summary(v, k) for k, v in root.items()]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch_by_id36, idfs) for idfs in chunked(id36s, 100))
