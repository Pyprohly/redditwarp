
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_SYNC import User as UserModel
    from ...models.moderated_subreddit_list import ModeratedSubredditListItem

from types import SimpleNamespace

from .get_partial_user_SYNC import GetPartialUser
from .bulk_fetch_partial_user_SYNC import BulkFetchPartialUser
from .pull_SYNC import Pull
from .pull_user_subreddits_SYNC import PullUserSubreddits
from ...models.load.user_SYNC import load_user
from ...models.load.moderated_subreddit_list import load_moderated_subreddit_list_item
from ... import http
from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_user_search_sync import SearchUsersListingPaginator

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
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return load_user(root['data'], self._client)

    def moderated_subreddits(self, user: str) -> Sequence[ModeratedSubredditListItem]:
        root = self._client.request('GET', f'/user/{user}/moderated_subreddits')
        return [load_moderated_subreddit_list_item(d) for d in root['data']]

    def explore(self, query: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[SearchUsersListingPaginator, SimpleNamespace]:
        p = SearchUsersListingPaginator(self._client, '/users/search', query)
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def exists(self, name: str) -> bool:
        return not self._client.request('GET', '/api/username_available', params={'user': name})
