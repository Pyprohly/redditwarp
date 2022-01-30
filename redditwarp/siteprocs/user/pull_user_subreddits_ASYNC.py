
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_ASYNC import Subreddit

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.implementations.user.async_ import UserSubredditListingAsyncPaginator

class PullUserSubreddits:
    def __init__(self, client: Client):
        self._client = client

    def popular(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingAsyncIterator[UserSubredditListingAsyncPaginator, Subreddit]:
        p = UserSubredditListingAsyncPaginator(self._client, '/users/popular')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def new(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingAsyncIterator[UserSubredditListingAsyncPaginator, Subreddit]:
        p = UserSubredditListingAsyncPaginator(self._client, '/users/new')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
