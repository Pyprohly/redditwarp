
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from .listing.mixins.sort_ASYNC import Sort
from .listing.subreddit_listing_async_paginator import SubredditListingAsyncPaginator
from ...models.subreddit_ASYNC import Subreddit

class SubredditSearchAsyncPaginator(
    Sort[Subreddit],
    SubredditListingAsyncPaginator,
):
    def __init__(self,
        client: Client,
        url: str,
        query: str,
        show_users: bool = False,
    ):
        super().__init__(client, url)
        self.query: str = query
        self.show_users: bool = show_users

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('q', self.query)
        if self.show_users:
            yield ('show_users', '1')
