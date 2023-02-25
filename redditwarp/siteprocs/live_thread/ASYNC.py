
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.live_thread_ASYNC import LiveThread, LiveUpdate

from ...models.live_thread import ContributorList, Contributor
from ...model_loaders.live_thread_ASYNC import load_live_thread, load_live_update
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...util.base_conversion import to_base36
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.live_thread_async1 import LiveUpdateListingAsyncPaginator
from ... import http

class LiveThreadProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def get(self, idt: str) -> Optional[LiveThread]:
        try:
            root = await self._client.request('GET', f'/live/{idt}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return load_live_thread(root['data'], self._client)

    def bulk_fetch(self, idts: Iterable[str]) -> CallChunkChainingAsyncIterator[LiveThread]:
        async def mass_fetch(idts: Sequence[str]) -> Sequence[LiveThread]:
            idts_str = ','.join(idts)
            root = await self._client.request('GET', '/api/live/by_id/' + idts_str)
            return [load_live_thread(o['data'], self._client) for o in root['data']['children']]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch, idfs) for idfs in chunked(idts, 100))

    async def create(self,
        title: str,
        description: str = '',
        resources: str = '',
        nsfw: bool = False,
    ) -> str:
        def g() -> Iterable[tuple[str, str]]:
            yield ('title', title)
            yield ('description', description)
            yield ('resources', resources)
            if nsfw: yield ('nsfw', '1')

        root = await self._client.request('POST', '/api/live/create', data=dict(g()))
        return root['json']['data']['id']

    async def config(self,
        idt: str,
        title: str,
        description: str = '',
        resources: str = '',
        nsfw: bool = False,
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            yield ('title', title)
            yield ('description', description)
            yield ('resources', resources)
            if nsfw: yield ('nsfw', '1')

        await self._client.request('POST', f'/api/live/{idt}/edit', data=dict(g()))

    async def close(self, idt: str) -> None:
        await self._client.request('POST', f'/api/live/{idt}/close_thread')

    async def get_update(self, idt: str, uuid: str) -> LiveUpdate:
        root = await self._client.request('GET', f'/live/{idt}/updates/{uuid}')
        return load_live_update(root['data'], self._client)

    def pull(self, idt: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[LiveUpdateListingAsyncPaginator, LiveUpdate]:
        p = LiveUpdateListingAsyncPaginator(self._client, f'/live/{idt}')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def create_update(self, idt: str, body: str) -> None:
        await self._client.request('POST', f'/api/live/{idt}/update', data={'body': body})

    async def strike_update(self, idt: str, uuid: str) -> None:
        await self._client.request('POST', f'/api/live/{idt}/strike_update', data={'id': 'LiveUpdate_' + uuid})

    async def delete_update(self, idt: str, uuid: str) -> None:
        await self._client.request('POST', f'/api/live/{idt}/delete_update', data={'id': 'LiveUpdate_' + uuid})

    async def list_contributors(self, idt: str) -> ContributorList:
        root = await self._client.request('GET', f'/live/{idt}/contributors')
        if isinstance(root, (dict, Mapping)):
            return ContributorList([Contributor(d) for d in root['data']['children']], ())

        contributors = [Contributor(d) for d in root[0]['data']['children']]
        invitations = [Contributor(d) for d in root[0]['data']['children']]
        return ContributorList(contributors, invitations)

    async def send_contributor_invite(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'type': 'liveupdate_contributor_invite',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        await self._client.request('POST', f'/api/live/{idt}/invite_contributor', data=data)

    async def accept_contributor_invite(self, idt: str) -> None:
        await self._client.request('POST', f'/api/live/{idt}/accept_contributor_invite')

    async def revoke_contributor_invite(self, idt: str, user_id: int) -> None:
        id36 = to_base36(user_id)
        await self._client.request('POST', f'/api/live/{idt}/rm_contributor_invite', data={'id': 't2_' + id36})

    async def leave_contributor(self, idt: str) -> None:
        await self._client.request('POST', f'/api/live/{idt}/leave_contributor')

    async def remove_contributor(self, idt: str, user_id: int) -> None:
        id36 = to_base36(user_id)
        await self._client.request('POST', f'/api/live/{idt}/rm_contributor', data={'id': 't2_' + id36})

    async def set_contributor_permissions(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'type': 'liveupdate_contributor',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        await self._client.request('POST', f'/api/live/{idt}/set_contributor_permissions', data=data)

    async def set_contributor_invite_permissions(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'type': 'liveupdate_contributor_invite',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        await self._client.request('POST', f'/api/live/{idt}/set_contributor_permissions', data=data)
