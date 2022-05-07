
from __future__ import annotations
from typing import Sequence

from .listing.listing_paginator import ListingPaginator
from ...models.live_thread_SYNC import LiveUpdate
from ...model_loaders.live_thread_SYNC import load_live_update

class LiveUpdateListingPaginator(ListingPaginator[LiveUpdate]):
    def fetch(self) -> Sequence[LiveUpdate]:
        data = self._fetch_data()
        return [load_live_update(d['data'], self.client) for d in data['children']]
