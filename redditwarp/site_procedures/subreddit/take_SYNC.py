
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...iterators.paginators.listing.subreddit_listing_paginator import SubredditListingPaginator

class Take:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        return self.new(amount)

    def default(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/default')
        return PaginatorChainingIterator(p, amount)

    def popular(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/popular')
        return PaginatorChainingIterator(p, amount)

    def new(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/new')
        return PaginatorChainingIterator(p, amount)

    def premium(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/premium')
        return PaginatorChainingIterator(p, amount)
