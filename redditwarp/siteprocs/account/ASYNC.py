
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Mapping, Any
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.my_account_ASYNC import MyAccount
    from ...models.user_relationship import UserRelationship, FriendRelationship
    from ...models.trophy import Trophy
    from ...models.karma_breakdown_entry import KarmaBreakdownEntry
    from ...types import JSON_ro

from .pull_subreddits_ASYNC import PullSubreddits
from ...model_loaders.my_account_ASYNC import load_account
from ...model_loaders.user_relationship import load_user_relationship, load_friend_relationship
from ...model_loaders.karma_breakdown_entry import load_karma_breakdown_entry
from ...model_loaders.trophy import load_trophy
from ...util.base_conversion import to_base36
from ... import exceptions
from ...http import exceptions as http_exceptions

class AccountProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull_subreddits: PullSubreddits = PullSubreddits(client)

    async def fetch(self) -> MyAccount:
        root = await self._client.request('GET', '/api/v1/me')
        if len(root) < 6:
            raise exceptions.RejectedResultException('no user context')
        return load_account(root, self._client)

    async def get_preferences(self) -> Mapping[str, Any]:
        return await self._client.request('GET', '/api/v1/me/prefs')

    async def set_preferences(self, prefs: Mapping[str, JSON_ro]) -> Mapping[str, Any]:
        return await self._client.request('PATCH', '/api/v1/me/prefs', json=prefs)

    async def get_karma_breakdown(self) -> Sequence[KarmaBreakdownEntry]:
        root = await self._client.request('GET', '/api/v1/me/karma')
        entries = root['data']
        return [load_karma_breakdown_entry(d) for d in entries]

    async def get_trophies(self) -> Sequence[Trophy]:
        root = await self._client.request('GET', '/api/v1/me/trophies')
        kind_data = root['data']['trophies']
        return [load_trophy(d['data']) for d in kind_data]

    async def get_friend(self, name: str) -> UserRelationship:
        root = await self._client.request('GET', f'/api/v1/me/friends/{name}')
        return load_user_relationship(root)

    async def friends(self) -> Sequence[UserRelationship]:
        try:
            root = await self._client.request('GET', '/api/v1/me/friends')

        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        entries = root['data']['children']
        return [load_user_relationship(d) for d in entries]

    async def add_friend(self, name: str, note: Optional[str] = None) -> FriendRelationship:
        json_data = {} if note is None else {'note': note}
        root = await self._client.request('PUT', f'/api/v1/me/friends/{name}', json=json_data)
        return load_friend_relationship(root)

    async def remove_friend(self, name: str) -> None:
        await self._client.request('DELETE', f'/api/v1/me/friends/{name}')

    async def blocked(self) -> Sequence[UserRelationship]:
        try:
            root = await self._client.request('GET', '/prefs/blocked')

        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        entries = root['data']['children']
        return [load_user_relationship(d) for d in entries]

    async def block_user_by_id(self, idn: int) -> None:
        await self._client.request('POST', '/api/block_user', data={'account_id': to_base36(idn)})

    async def block_user_by_name(self, name: str) -> None:
        await self._client.request('POST', '/api/block_user', data={'name': name})

    async def unblock_user_by_target_id(self, target_id: int, agent_id: int) -> None:
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_id),
            'id': 't2_' + to_base36(target_id),
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def unblock_user_by_target_name(self, target_name: str, agent_id: int) -> None:
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_id),
            'name': target_name,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def trusted(self) -> Sequence[UserRelationship]:
        try:
            root = await self._client.request('GET', '/prefs/trusted')

        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        entries = root['data']['children']
        return [load_user_relationship(d) for d in entries]

    async def add_trusted_user(self, name: str) -> None:
        await self._client.request('POST', '/api/add_whitelisted', params={'name': name})

    async def remove_trusted_user(self, name: str) -> None:
        await self._client.request('POST', '/api/remove_whitelisted', params={'name': name})

    async def messaging(self) -> tuple[Sequence[UserRelationship], Sequence[UserRelationship]]:
        try:
            root = await self._client.request('GET', '/prefs/messaging')

        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        blocked_entries = root[0]['data']['children']
        trusted_entries = root[1]['data']['children']
        return (
            [load_user_relationship(d) for d in blocked_entries],
            [load_user_relationship(d) for d in trusted_entries],
        )
