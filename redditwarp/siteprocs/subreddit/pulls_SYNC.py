
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_account_pull_subreddits_sync import SubredditListingPaginator

class Pulls:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[SubredditListingPaginator, Subreddit]:
        return self.popular(amount)

    def popular(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/popular')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def new(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/new')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def default(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/default')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def premium(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[SubredditListingPaginator, Subreddit]:
        p = SubredditListingPaginator(self._client, '/subreddits/premium')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
