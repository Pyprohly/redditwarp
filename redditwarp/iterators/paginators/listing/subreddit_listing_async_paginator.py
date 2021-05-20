
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....models.subreddit_ASYNC import Subreddit
from ....models.load.subreddit_ASYNC import load_subreddit

class SubredditListingAsyncPaginator(ListingAsyncPaginator[Subreddit]):
    async def _fetch_result(self) -> Sequence[Subreddit]:
        data = await self._fetch_data()
        return [load_subreddit(d['data'], self.client) for d in data['children']]
