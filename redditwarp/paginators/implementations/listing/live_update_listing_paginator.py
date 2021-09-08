
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.live_thread_SYNC import LiveUpdate
from ....models.load.live_thread_SYNC import load_live_update

class LiveUpdateListingPaginator(ListingPaginator[LiveUpdate]):
    def next_result(self) -> Sequence[LiveUpdate]:
        data = self._fetch_data()
        return [load_live_update(d['data'], self.client) for d in data['children']]
