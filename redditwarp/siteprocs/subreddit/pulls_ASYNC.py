
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_ASYNC import Subreddit

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.listing.subreddit_listing_async_paginator import SubredditListingAsyncPaginator

class Pulls:
    def __init__(self, client: Client) -> None:
        self._client = client

    def popular(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[SubredditListingAsyncPaginator, Subreddit]:
        p = SubredditListingAsyncPaginator(self._client, '/subreddits/popular')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def new(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[SubredditListingAsyncPaginator, Subreddit]:
        p = SubredditListingAsyncPaginator(self._client, '/subreddits/new')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def default(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[SubredditListingAsyncPaginator, Subreddit]:
        p = SubredditListingAsyncPaginator(self._client, '/subreddits/default')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def premium(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[SubredditListingAsyncPaginator, Subreddit]:
        p = SubredditListingAsyncPaginator(self._client, '/subreddits/premium')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
