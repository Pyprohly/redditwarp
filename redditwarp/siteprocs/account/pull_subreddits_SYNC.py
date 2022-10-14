
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.account_sync1 import (
    SubscribedListingPaginator,
    ContributingListingPaginator,
    ModeratingListingPaginator,
)

class PullSubreddits:
    def __init__(self, client: Client) -> None:
        self._client = client

    def subscribed(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingIterator[SubscribedListingPaginator, Subreddit]:
        """Pull subreddits the current user is subscribed to."""
        p = SubscribedListingPaginator(self._client, '/subreddits/mine/subscriber')
        return ImpartedPaginatorChainingIterator(p, amount)

    def contributing(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingIterator[ContributingListingPaginator, Subreddit]:
        """Pull subreddits the current user is an approved user in."""
        p = ContributingListingPaginator(self._client, '/subreddits/mine/contributor')
        return ImpartedPaginatorChainingIterator(p, amount)

    def moderating(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingIterator[ModeratingListingPaginator, Subreddit]:
        """Pull subreddits the current user is a moderator of."""
        p = ModeratingListingPaginator(self._client, '/subreddits/mine/moderator')
        return ImpartedPaginatorChainingIterator(p, amount)
