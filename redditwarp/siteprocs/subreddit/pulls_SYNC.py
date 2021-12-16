
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...paginators.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...paginators.listing.subreddit_listing_paginator_sync import SubredditListingPaginator

class Pulls:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        return self.popular(amount)

    def popular(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/popular')
        return ImpartedPaginatorChainingIterator(p, amount)

    def new(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/new')
        return ImpartedPaginatorChainingIterator(p, amount)

    def default(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/default')
        return ImpartedPaginatorChainingIterator(p, amount)

    def premium(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/premium')
        return ImpartedPaginatorChainingIterator(p, amount)
