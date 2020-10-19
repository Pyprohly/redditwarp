
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Tuple
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.account_SYNC import MyAccount
    from ....models.user_list_item import UserListItem

from .pull_subreddits_SYNC import PullSubreddits
from ...load.account_SYNC import load_account
from ...load.user_list_item import load_user_list_item
from .... import exceptions

class Account:
    def __init__(self, client: Client):
        self._client = client
        self.pull_subreddits = PullSubreddits(client)

    def fetch(self) -> MyAccount:
        root = self._client.request('GET', '/api/v1/me')
        if len(root) < 3:
            raise RuntimeError('no user context')
        return load_account(root, self._client)

    def friends(self) -> Sequence[UserListItem]:
        root = self._client.request('GET', '/api/v1/me/friends')
        entries = root['data']['children']
        return [load_user_list_item(obj_data) for obj_data in entries]

    def get_friend(self, name: str) -> Optional[UserListItem]:
        try:
            root = self._client.request('GET', f'/api/v1/me/friends/{name}')
        except exceptions.Variant1RedditAPIError as e:
            if e.codename == 'USER_DOESNT_EXIST':
                return None
            raise
        return load_user_list_item(root)

    def blocked(self) -> Sequence[UserListItem]:
        root = self._client.request('GET', '/prefs/blocked')
        entries = root['data']['children']
        return [load_user_list_item(obj_data) for obj_data in entries]

    def trusted(self) -> Tuple[Sequence[UserListItem], Sequence[UserListItem]]:
        root = self._client.request('GET', '/prefs/messaging')
        blocked_entries = root[0]['data']['children']
        whitelisted_entries = root[1]['data']['children']
        blocked_list = [load_user_list_item(obj_data) for obj_data in blocked_entries]
        whitelisted_list = [load_user_list_item(obj_data) for obj_data in whitelisted_entries]
        return (blocked_list, whitelisted_list)
