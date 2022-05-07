
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_SYNC import User
    from ...models.moderated_subreddit import ModeratedSubreddit

from .get_user_summary_SYNC import GetUserSummary
from .bulk_fetch_user_summary_SYNC import BulkFetchUserSummary
from .pull_SYNC import Pull
from .pull_user_subreddits_SYNC import PullUserSubreddits
from ...model_loaders.user_SYNC import load_user
from ...model_loaders.moderated_subreddit import load_moderated_subreddit
from ... import http
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.user.sync1 import SearchUsersListingPaginator

class UserProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.get_user_summary: GetUserSummary = GetUserSummary(client)
        self.bulk_fetch_user_summary: BulkFetchUserSummary = BulkFetchUserSummary(client)
        self.pull: Pull = Pull(client)
        self.pull_user_subreddits: PullUserSubreddits = PullUserSubreddits(client)

    def get_by_name(self, name: str) -> Optional[User]:
        if not name:
            raise ValueError('`name` must not be empty')
        try:
            root = self._client.request('GET', f'/user/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return load_user(root['data'], self._client)

    def moderated_subreddits(self, user: str) -> Sequence[ModeratedSubreddit]:
        root = self._client.request('GET', f'/user/{user}/moderated_subreddits')
        return [load_moderated_subreddit(d) for d in root['data']]

    def search(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SearchUsersListingPaginator, User]:
        p = SearchUsersListingPaginator(self._client, '/users/search', query)
        return ImpartedPaginatorChainingIterator(p, amount)

    def name_exists(self, name: str) -> bool:
        return not self._client.request('GET', '/api/username_available', params={'user': name})
