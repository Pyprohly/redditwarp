
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_account_pull_subreddits_sync import (
    SubscribedListingPaginator,
    ContributingListingPaginator,
    ModeratingListingPaginator,
)

class PullSubreddits:
    def __init__(self, client: Client):
        self._client = client

    def subscribed(self, amount: Optional[int] = None
            ) -> PaginatorChainingWrapper[SubscribedListingPaginator, Subreddit]:
        p = SubscribedListingPaginator(self._client, '/subreddits/mine/subscriber')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def contributing(self, amount: Optional[int] = None
            ) -> PaginatorChainingWrapper[ContributingListingPaginator, Subreddit]:
        p = ContributingListingPaginator(self._client, '/subreddits/mine/contributor')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def moderating(self, amount: Optional[int] = None
            ) -> PaginatorChainingWrapper[ModeratingListingPaginator, Subreddit]:
        p = ModeratingListingPaginator(self._client, '/subreddits/mine/moderator')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
