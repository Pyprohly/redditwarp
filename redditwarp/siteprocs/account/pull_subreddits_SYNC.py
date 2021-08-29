
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.account_pull_subreddits_sync import (
    SubscribedListingPaginator,
    ContributingListingPaginator,
    ModeratingListingPaginator,
)

class PullSubreddits:
    def __init__(self, client: Client):
        self._client = client

    def subscribed(self, amount: Optional[int] = None
            ) -> PaginatorChainingIterator[SubscribedListingPaginator, Subreddit]:
        p = SubscribedListingPaginator(self._client, '/subreddits/mine/subscriber')
        return PaginatorChainingIterator(p, amount)

    def contributing(self, amount: Optional[int] = None
            ) -> PaginatorChainingIterator[ContributingListingPaginator, Subreddit]:
        p = ContributingListingPaginator(self._client, '/subreddits/mine/contributor')
        return PaginatorChainingIterator(p, amount)

    def moderating(self, amount: Optional[int] = None
            ) -> PaginatorChainingIterator[ModeratingListingPaginator, Subreddit]:
        p = ModeratingListingPaginator(self._client, '/subreddits/mine/moderator')
        return PaginatorChainingIterator(p, amount)
