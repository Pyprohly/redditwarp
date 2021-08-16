
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.live_thread import LiveThreadUpdate
from ....models.load.live_thread import load_live_thread_update

class LiveThreadUpdateListingPaginator(ListingPaginator[LiveThreadUpdate]):
    def fetch_next_result(self) -> Sequence[LiveThreadUpdate]:
        data = self._fetch_data()
        return [load_live_thread_update(d['data']) for d in data['children']]
