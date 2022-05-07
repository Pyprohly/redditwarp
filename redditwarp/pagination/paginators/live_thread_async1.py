
from __future__ import annotations
from typing import Sequence

from .listing.listing_async_paginator import ListingAsyncPaginator
from ...models.live_thread_ASYNC import LiveUpdate
from ...model_loaders.live_thread_ASYNC import load_live_update

class LiveUpdateListingAsyncPaginator(ListingAsyncPaginator[LiveUpdate]):
    async def fetch(self) -> Sequence[LiveUpdate]:
        data = await self._fetch_data()
        return [load_live_update(d['data'], self.client) for d in data['children']]
