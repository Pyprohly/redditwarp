
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client

from .listing.mixins.sort_SYNC import Sort
from .listing.subreddit_listing_paginator import SubredditListingPaginator
from ...models.subreddit_SYNC import Subreddit

class SubredditSearchPaginator(
    Sort[Subreddit],
    SubredditListingPaginator,
):
    def __init__(self,
        client: Client,
        url: str,
        query: str,
        show_users: bool = False,
    ) -> None:
        super().__init__(client, url)
        self.query: str = query
        self.show_users: bool = show_users

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('q', self.query)
        if self.show_users:
            yield ('show_users', '1')
