
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.user_ASYNC import User
    from ...models.moderated_subreddit import ModeratedSubreddit

from .get_user_summary_ASYNC import GetUserSummary
from .bulk_fetch_user_summary_ASYNC import BulkFetchUserSummary
from .pull_ASYNC import Pull
from .pull_user_subreddits_ASYNC import PullUserSubreddits
from ...model_loaders.user_ASYNC import load_user
from ...model_loaders.moderated_subreddit import load_moderated_subreddit
from ... import http
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.user.async1 import SearchUsersListingAsyncPaginator

class UserProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.get_user_summary: GetUserSummary = GetUserSummary(client)
        self.bulk_fetch_user_summary: BulkFetchUserSummary = BulkFetchUserSummary(client)
        self.pull: Pull = Pull(client)
        self.pull_user_subreddits: PullUserSubreddits = PullUserSubreddits(client)

    async def get_by_name(self, name: str) -> Optional[User]:
        if not name:
            raise ValueError('`name` must not be empty')
        try:
            root = await self._client.request('GET', f'/user/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return load_user(root['data'], self._client)

    async def moderated_subreddits(self, user: str) -> Sequence[ModeratedSubreddit]:
        root = await self._client.request('GET', f'/user/{user}/moderated_subreddits')
        return [load_moderated_subreddit(d) for d in root['data']]

    def search(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[SearchUsersListingAsyncPaginator, User]:
        p = SearchUsersListingAsyncPaginator(self._client, '/users/search', query)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def name_exists(self, name: str) -> bool:
        return not await self._client.request('GET', '/api/username_available', params={'user': name})
