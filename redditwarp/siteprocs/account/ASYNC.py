
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Tuple, Mapping, Any
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.my_account_ASYNC import MyAccount
    from ...models.user_relationship_item import UserRelationshipItem, FriendRelationshipItem
    from ...models.trophy import Trophy
    from ...models.karma_breakdown_entry import KarmaBreakdownEntry

from .pull_subreddits_ASYNC import PullSubreddits
from ...model_loaders.my_account_ASYNC import load_account
from ...model_loaders.user_relationship_item import load_user_relationship_item, load_friend_relationship_item
from ...model_loaders.karma_breakdown_entry import load_karma_breakdown_entry
from ...model_loaders.trophy import load_trophy
from ... import exceptions
from ...util.base_conversion import to_base36

class AccountProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.pull_subreddits: PullSubreddits = PullSubreddits(client)

    async def fetch(self) -> MyAccount:
        root = await self._client.request('GET', '/api/v1/me')
        if len(root) < 3:
            raise RuntimeError('no user context')
        return load_account(root, self._client)

    async def get_preferences(self) -> Mapping[str, Any]:
        return await self._client.request('GET', '/api/v1/me/prefs')

    async def set_preferences(self, json_dict: Mapping[str, Any]) -> Mapping[str, Any]:
        return await self._client.request('PATCH', '/api/v1/me/prefs', json=json_dict)

    async def get_karma_breakdown(self) -> Sequence[KarmaBreakdownEntry]:
        root = await self._client.request('GET', '/api/v1/me/karma')
        entries = root['data']
        return [load_karma_breakdown_entry(d) for d in entries]

    async def get_trophies(self) -> Sequence[Trophy]:
        root = await self._client.request('GET', '/api/v1/me/trophies')
        kind_data = root['data']['trophies']
        return [load_trophy(d['data']) for d in kind_data]

    async def get_friend(self, name: str) -> Optional[UserRelationshipItem]:
        try:
            root = await self._client.request('GET', f'/api/v1/me/friends/{name}')
        except exceptions.RedditError as e:
            if e.codename == 'USER_DOESNT_EXIST':
                return None
            raise
        return load_user_relationship_item(root)

    async def friends(self) -> Sequence[UserRelationshipItem]:
        root = await self._client.request('GET', '/api/v1/me/friends')
        entries = root['data']['children']
        return [load_user_relationship_item(d) for d in entries]

    async def add_friend(self, name: str, note: Optional[str] = None) -> FriendRelationshipItem:
        json_data = {} if note is None else {'note': note}
        root = await self._client.request('PUT', f'/api/v1/me/friends/{name}', json=json_data)
        return load_friend_relationship_item(root)

    async def remove_friend(self, name: str) -> bool:
        try:
            await self._client.request('DELETE', f'/api/v1/me/friends/{name}')
        except exceptions.RedditError as e:
            if e.codename == 'NOT_FRIEND':
                return False
            raise
        return True

    async def blocked(self) -> Sequence[UserRelationshipItem]:
        root = await self._client.request('GET', '/prefs/blocked')
        entries = root['data']['children']
        return [load_user_relationship_item(d) for d in entries]

    async def block_user_by_name(self, name: str) -> None:
        await self._client.request('POST', '/api/block_user', data={'name': name})

    async def block_user_by_id(self, idn: int) -> None:
        await self._client.request('POST', '/api/block_user', data={'account_id': to_base36(idn)})

    async def unblock_user_by_target_name(self, agent_idn: int, target_name: str) -> None:
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_idn),
            'name': target_name,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def unblock_user_by_target_id(self, agent_idn: int, target_id: int) -> None:
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_idn),
            'id': 't2_' + to_base36(target_id),
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def trusted(self) -> Sequence[UserRelationshipItem]:
        root = await self._client.request('GET', '/prefs/trusted')
        entries = root['data']['children']
        return [load_user_relationship_item(d) for d in entries]

    async def add_trusted_user(self, name: str) -> None:
        await self._client.request('POST', '/api/add_whitelisted', params={'name': name})

    async def remove_trusted_user(self, name: str) -> None:
        await self._client.request('POST', '/api/remove_whitelisted', params={'name': name})

    async def messaging(self) -> Tuple[Sequence[UserRelationshipItem], Sequence[UserRelationshipItem]]:
        root = await self._client.request('GET', '/prefs/messaging')
        blocked_entries = root[0]['data']['children']
        trusted_entries = root[1]['data']['children']
        return (
            [load_user_relationship_item(d) for d in blocked_entries],
            [load_user_relationship_item(d) for d in trusted_entries],
        )
