
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Tuple
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.account_SYNC import MyAccount
    from ....models.user_list_item import UserListItem, FriendUserListItem
    from ....models.trophy import Trophy
    from ....models.karma_breakdown_item import KarmaBreakdownItem

from .pull_subreddits_SYNC import PullSubreddits
from ...load.account_SYNC import load_account
from ...load.user_list_item import load_user_list_item, load_friend_user_list_item
from ...load.karma_breakdown_item import load_karma_breakdown_item
from ...load.trophy import load_trophy
from .... import exceptions

class Account:
    def __init__(self, client: Client):
        self._client = client
        self.pull_subreddits = PullSubreddits(client)

    def fetch_identity(self) -> MyAccount:
        root = self._client.request('GET', '/api/v1/me')
        if len(root) < 3:
            raise RuntimeError('no user context')
        return load_account(root, self._client)

    def friends(self) -> Sequence[UserListItem]:
        root = self._client.request('GET', '/api/v1/me/friends')
        entries = root['data']['children']
        return [load_user_list_item(d) for d in entries]

    def blocked(self) -> Sequence[UserListItem]:
        root = self._client.request('GET', '/prefs/blocked')
        entries = root['data']['children']
        return [load_user_list_item(d) for d in entries]

    def trusted(self) -> Sequence[UserListItem]:
        root = self._client.request('GET', '/prefs/trusted')
        entries = root['data']['children']
        return [load_user_list_item(d) for d in entries]

    def messaging(self) -> Tuple[Sequence[UserListItem], Sequence[UserListItem]]:
        root = self._client.request('GET', '/prefs/messaging')
        blocked_entries = root[0]['data']['children']
        trusted_entries = root[1]['data']['children']
        return (
            [load_user_list_item(d) for d in blocked_entries],
            [load_user_list_item(d) for d in trusted_entries],
        )

    def get_karma_breakdown(self) -> Sequence[KarmaBreakdownItem]:
        root = self._client.request('GET', '/api/v1/me/karma')
        entries = root['data']
        return [load_karma_breakdown_item(d) for d in entries]

    def get_trophies(self) -> Sequence[Trophy]:
        root = self._client.request('GET', '/api/v1/me/trophies')
        kind_data = root['data']['trophies']
        return [load_trophy(d['data']) for d in kind_data]

    def get_friend(self, name: str) -> Optional[UserListItem]:
        try:
            root = self._client.request('GET', f'/api/v1/me/friends/{name}')
        except exceptions.Variant1RedditAPIError as e:
            if e.codename == 'USER_DOESNT_EXIST':
                return None
            raise
        return load_user_list_item(root)

    def add_friend(self, name: str, note: Optional[str] = None) -> FriendUserListItem:
        json_data = {} if note is None else {'note': note}
        root = self._client.request('PUT', f'api/v1/me/friends/{name}', json=json_data)
        return load_friend_user_list_item(root)

    def delete_friend(self, name: str) -> bool:
        try:
            self._client.request('DELETE', f'/api/v1/me/friends/{name}')
        except exceptions.Variant1RedditAPIError as e:
            if e.codename == 'NOT_FRIEND':
                return False
            raise
        return True

    def add_trusted_user(self, name: str) -> None:
        self._client.request('POST', '/api/add_whitelisted', params={'name': name})

    def remove_trusted_user(self, name: str) -> None:
        self._client.request('POST', '/api/remove_whitelisted', params={'name': name})
