
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.subreddit_SYNC import Subreddit

from ....iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ....iterators.paginators.listing.subreddit_listing_paginator import SubredditListingPaginator

class PullSubreddits:
    def __init__(self, client: Client):
        self._client = client

    def subscribed(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/mine/subscriber')
        return PaginatorChainingIterator(p, amount)

    def contributing(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/mine/contributor')
        return PaginatorChainingIterator(p, amount)

    def moderating(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/mine/moderator')
        return PaginatorChainingIterator(p, amount)
