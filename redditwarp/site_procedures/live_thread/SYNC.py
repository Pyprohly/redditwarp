
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.live_thread import LiveThread as LiveThreadModel, LiveThreadUpdate

from ...models.live_thread import ContributorsList, ContributorInfo
from ...models.load.live_thread import load_live_thread, load_live_thread_update
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk_SYNC import CallChunk
from ...util.base_conversion import to_base36
from ...iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...iterators.paginators.listing.live_thread_update_listing_paginator import LiveThreadUpdateListingPaginator
from ... import exceptions

class LiveThread:
    def __init__(self, client: Client):
        self._client = client

    def get(self, idt: str) -> Optional[LiveThreadModel]:
        try:
            root = self._client.request('GET', f'/live/{idt}/about')
        except exceptions.HTTPStatusError as e:
            if e.response.status == 404:
                return None
            raise
        return load_live_thread(root['data'])

    def bulk_fetch(self, idts: Iterable[str]) -> CallChunkChainingIterator[str, LiveThreadModel]:
        def mass_fetch(idts: Sequence[str]) -> Sequence[LiveThreadModel]:
            idts_str = ','.join(idts)
            root = self._client.request('GET', '/api/live/by_id/' + idts_str)
            return [load_live_thread(o['data']) for o in root['data']['children']]

        return CallChunkChainingIterator(
                CallChunk(mass_fetch, idfs) for idfs in chunked(idts, 100))

    def create(self, title: str, description: str = '', resources: str = '', *, nsfw: bool = False) -> str:
        form_data = {
            'title': title,
            'description': description,
            'resources': resources,
        }
        if nsfw:
            form_data['nsfw'] = '1'

        root = self._client.request('GET', '/api/live/create', data=form_data)
        return root['json']['data']['id']

    def configure(self, idt: str, title: str, description: str, resources: str, nsfw: bool) -> None:
        form_data = {
            'title': title,
            'description': description,
            'resources': resources,
            'nsfw': '01'[nsfw],
        }
        self._client.request('GET', f'/api/live/{idt}/edit', data=form_data)

    def close(self, idt: str) -> None:
        self._client.request('GET', f'/api/live/{idt}/close_thread')

    def get_thread_update(self, idt: str, update_uuid: str) -> LiveThreadUpdate:
        root = self._client.request('GET', f'/live/{idt}/updates/{update_uuid}')
        return load_live_thread_update(root['data'])

    def pull(self, idt: str, amount: Optional[int] = None) -> PaginatorChainingIterator[LiveThreadUpdateListingPaginator, LiveThreadUpdate]:
        p = LiveThreadUpdateListingPaginator(self._client, f'/live/{idt}')
        return PaginatorChainingIterator(p, amount)

    def post_live_update(self, idt: str, body: str) -> None:
        self._client.request('POST', f'/api/live/{idt}/update', data={'body': body})

    def strike_live_update(self, idt: str, update_uuid: str) -> None:
        self._client.request('POST', f'/api/live/{idt}/strike_update', data={'id': 'LiveUpdate_' + update_uuid})

    def delete_live_update(self, idt: str, update_uuid: str) -> None:
        self._client.request('POST', f'/api/live/{idt}/delete_update', data={'id': 'LiveUpdate_' + update_uuid})

    def list_contributors(self, idt: str) -> ContributorsList:
        root = self._client.request('GET', f'/live/{idt}/contributors')
        if isinstance(root, Mapping):
            return ContributorsList([ContributorInfo(d) for d in root['data']['children']], ())

        contributors = [ContributorInfo(d) for d in root[0]['data']['children']]
        invitations = [ContributorInfo(d) for d in root[0]['data']['children']]
        return ContributorsList(contributors, invitations)

    def send_contributor_invite(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'type': 'liveupdate_contributor_invite',
            'name': user,
            'permissions': ','.join('+' + i for i in permissions),
        }
        self._client.request('POST', f'/api/live/{idt}/invite_contributor', data=data)

    def accept_contributor_invite(self, idt: str) -> None:
        self._client.request('POST', f'/api/live/{idt}/accept_contributor_invite')

    def revoke_contributor_invite(self, idt: str, user_id36: int) -> None:
        id36 = to_base36(user_id36)
        self._client.request('POST', f'/api/live/{idt}/rm_contributor_invite', data={'id': 't2_' + id36})

    def leave_contributor(self, idt: str) -> None:
        self._client.request('POST', f'/api/live/{idt}/leave_contributor')

    def remove_contributor(self, idt: str, user_id36: int) -> None:
        id36 = to_base36(user_id36)
        self._client.request('POST', f'/api/live/{idt}/rm_contributor', data={'id': 't2_' + id36})

    def set_contributor_permissions(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'type': 'liveupdate_contributor',
            'name': user,
            'permissions': ','.join('+' + i for i in permissions),
        }
        self._client.request('POST', f'/api/live/{idt}/set_contributor_permissions', data=data)

    def set_contributor_invite_permissions(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'type': 'liveupdate_contributor_invite',
            'name': user,
            'permissions': ','.join('+' + i for i in permissions),
        }
        self._client.request('POST', f'/api/live/{idt}/set_contributor_permissions', data=data)
