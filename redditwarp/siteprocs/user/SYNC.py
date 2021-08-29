
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_SYNC import User as UserModel
    from ...models.moderated_subreddit_list_item import ModeratedSubredditListItem

from .get_partial_user_SYNC import GetPartialUser
from .bulk_fetch_partial_user_SYNC import BulkFetchPartialUser
from .pull_SYNC import Pull
from .pull_user_subreddits_SYNC import PullUserSubreddits
from ...models.load.user_SYNC import load_user
from ...models.load.moderated_subreddit_list_item import load_moderated_subreddit_list_item
from ... import exceptions

class User:
    def __init__(self, client: Client):
        self._client = client
        self.get_partial_user = GetPartialUser(client)
        self.bulk_fetch_partial_user = BulkFetchPartialUser(client)
        self.pull = Pull(client)
        self.pull_user_subreddits = PullUserSubreddits(client)

    def get_by_name(self, name: str) -> Optional[UserModel]:
        try:
            root = self._client.request('GET', f'/user/{name}/about')
        except exceptions.HTTPStatusError as e:
            if e.response.status == 404:
                return None
            raise
        return load_user(root['data'], self._client)

    def moderated_subreddits(self, user: str) -> Sequence[ModeratedSubredditListItem]:
        root = self._client.request('GET', f'/user/{user}/moderated_subreddits')
        return [load_moderated_subreddit_list_item(d) for d in root['data']]
