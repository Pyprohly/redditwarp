
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....models.live_thread_ASYNC import LiveUpdate
from ....models.load.live_thread_ASYNC import load_live_update

class LiveUpdateListingAsyncPaginator(ListingAsyncPaginator[LiveUpdate]):
    async def next_result(self) -> Sequence[LiveUpdate]:
        data = await self._next_data()
        return [load_live_update(d['data'], self.client) for d in data['children']]
