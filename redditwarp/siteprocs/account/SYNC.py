
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Tuple, Mapping, Any
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.my_account_SYNC import MyAccount
    from ...models.user_relationship_item import UserRelationshipItem, FriendRelationshipItem
    from ...models.trophy import Trophy
    from ...models.karma_breakdown_entry import KarmaBreakdownEntry

from .pull_subreddits_SYNC import PullSubreddits
from ...model_loaders.my_account_SYNC import load_account
from ...model_loaders.user_relationship_item import load_user_relationship_item, load_friend_relationship_item
from ...model_loaders.karma_breakdown_entry import load_karma_breakdown_entry
from ...model_loaders.trophy import load_trophy
from ... import exceptions
from ...util.base_conversion import to_base36
from ...exceptions import RejectedResultException

class AccountProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.pull_subreddits: PullSubreddits = PullSubreddits(client)

    def fetch(self) -> MyAccount:
        root = self._client.request('GET', '/api/v1/me')
        if len(root) < 6:
            raise RejectedResultException('no user context')
        return load_account(root, self._client)

    def get_preferences(self) -> Mapping[str, Any]:
        return self._client.request('GET', '/api/v1/me/prefs')

    def set_preferences(self, json_dict: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._client.request('PATCH', '/api/v1/me/prefs', json=json_dict)

    def get_karma_breakdown(self) -> Sequence[KarmaBreakdownEntry]:
        root = self._client.request('GET', '/api/v1/me/karma')
        entries = root['data']
        return [load_karma_breakdown_entry(d) for d in entries]

    def get_trophies(self) -> Sequence[Trophy]:
        root = self._client.request('GET', '/api/v1/me/trophies')
        kind_data = root['data']['trophies']
        return [load_trophy(d['data']) for d in kind_data]

    def get_friend(self, name: str) -> Optional[UserRelationshipItem]:
        try:
            root = self._client.request('GET', f'/api/v1/me/friends/{name}')
        except exceptions.RedditError as e:
            if e.codename == 'USER_DOESNT_EXIST':
                return None
            raise
        return load_user_relationship_item(root)

    def friends(self) -> Sequence[UserRelationshipItem]:
        root = self._client.request('GET', '/api/v1/me/friends')
        entries = root['data']['children']
        return [load_user_relationship_item(d) for d in entries]

    def add_friend(self, name: str, note: Optional[str] = None) -> FriendRelationshipItem:
        json_data = {} if note is None else {'note': note}
        root = self._client.request('PUT', f'/api/v1/me/friends/{name}', json=json_data)
        return load_friend_relationship_item(root)

    def remove_friend(self, name: str) -> bool:
        try:
            self._client.request('DELETE', f'/api/v1/me/friends/{name}')
        except exceptions.RedditError as e:
            if e.codename == 'NOT_FRIEND':
                return False
            raise
        return True

    def blocked(self) -> Sequence[UserRelationshipItem]:
        root = self._client.request('GET', '/prefs/blocked')
        entries = root['data']['children']
        return [load_user_relationship_item(d) for d in entries]

    def block_user_by_name(self, name: str) -> None:
        self._client.request('POST', '/api/block_user', data={'name': name})

    def block_user_by_id(self, idn: int) -> None:
        self._client.request('POST', '/api/block_user', data={'account_id': to_base36(idn)})

    def unblock_user_by_target_name(self, agent_idn: int, target_name: str) -> None:
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_idn),
            'name': target_name,
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def unblock_user_by_target_id(self, agent_idn: int, target_id: int) -> None:
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_idn),
            'id': 't2_' + to_base36(target_id),
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def trusted(self) -> Sequence[UserRelationshipItem]:
        root = self._client.request('GET', '/prefs/trusted')
        entries = root['data']['children']
        return [load_user_relationship_item(d) for d in entries]

    def add_trusted_user(self, name: str) -> None:
        self._client.request('POST', '/api/add_whitelisted', params={'name': name})

    def remove_trusted_user(self, name: str) -> None:
        self._client.request('POST', '/api/remove_whitelisted', params={'name': name})

    def messaging(self) -> Tuple[Sequence[UserRelationshipItem], Sequence[UserRelationshipItem]]:
        root = self._client.request('GET', '/prefs/messaging')
        blocked_entries = root[0]['data']['children']
        trusted_entries = root[1]['data']['children']
        return (
            [load_user_relationship_item(d) for d in blocked_entries],
            [load_user_relationship_item(d) for d in trusted_entries],
        )
