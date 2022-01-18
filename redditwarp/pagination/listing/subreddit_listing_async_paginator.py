
from __future__ import annotations
from typing import Sequence

from ..listing.listing_async_paginator import ListingAsyncPaginator
from ...models.load.subreddit_ASYNC import load_subreddit
from ...models.subreddit_ASYNC import Subreddit

class SubredditListingAsyncPaginator(ListingAsyncPaginator[Subreddit]):
    async def fetch(self) -> Sequence[Subreddit]:
        data = await self._fetch_data()
        return [load_subreddit(d['data'], self.client) for d in data['children']]
