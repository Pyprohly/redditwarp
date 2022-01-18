
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_ASYNC import Subreddit

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.implementations.account_async import (
    SubscribedListingAsyncPaginator,
    ContributingListingAsyncPaginator,
    ModeratingListingAsyncPaginator,
)

class PullSubreddits:
    def __init__(self, client: Client):
        self._client = client

    def subscribed(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingAsyncIterator[SubscribedListingAsyncPaginator, Subreddit]:
        p = SubscribedListingAsyncPaginator(self._client, '/subreddits/mine/subscriber')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def contributing(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingAsyncIterator[ContributingListingAsyncPaginator, Subreddit]:
        p = ContributingListingAsyncPaginator(self._client, '/subreddits/mine/contributor')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def moderating(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingAsyncIterator[ModeratingListingAsyncPaginator, Subreddit]:
        p = ModeratingListingAsyncPaginator(self._client, '/subreddits/mine/moderator')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
