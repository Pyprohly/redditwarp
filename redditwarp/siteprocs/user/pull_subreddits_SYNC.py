
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_SYNC import Subreddit

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.user.sync1 import UserSubredditListingPaginator

class PullSubreddits:
    def __init__(self, client: Client) -> None:
        self._client = client

    def popular(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingIterator[UserSubredditListingPaginator, Subreddit]:
        p = UserSubredditListingPaginator(self._client, '/users/popular')
        return ImpartedPaginatorChainingIterator(p, amount)

    def new(self, amount: Optional[int] = None
            ) -> ImpartedPaginatorChainingIterator[UserSubredditListingPaginator, Subreddit]:
        p = UserSubredditListingPaginator(self._client, '/users/new')
        return ImpartedPaginatorChainingIterator(p, amount)
