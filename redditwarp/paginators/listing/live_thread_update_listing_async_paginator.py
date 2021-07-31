
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ...models.live_thread import LiveThreadUpdate
from ...models.load.live_thread import load_live_thread_update

class LiveThreadUpdateListingAsyncPaginator(ListingAsyncPaginator[LiveThreadUpdate]):
    async def _fetch_result(self) -> Sequence[LiveThreadUpdate]:
        data = await self._fetch_data()
        return [load_live_thread_update(d['data']) for d in data['children']]
