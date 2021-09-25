
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_user_pull_subreddits_sync import UserSubredditListingPaginator

class PullUserSubreddits:
    def __init__(self, client: Client):
        self._client = client

    def popular(self, amount: Optional[int] = None
            ) -> PaginatorChainingWrapper[UserSubredditListingPaginator, Subreddit]:
        p = UserSubredditListingPaginator(self._client, '/users/popular')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def new(self, amount: Optional[int] = None
            ) -> PaginatorChainingWrapper[UserSubredditListingPaginator, Subreddit]:
        p = UserSubredditListingPaginator(self._client, '/users/new')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
