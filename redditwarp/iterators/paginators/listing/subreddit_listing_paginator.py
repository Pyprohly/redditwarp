
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.subreddit_SYNC import Subreddit
from ....api.load.subreddit_SYNC import load_subreddit

class SubredditListingPaginator(ListingPaginator[Subreddit]):
    def _fetch_result(self) -> Sequence[Subreddit]:
        data = self._fetch_data()
        return [load_subreddit(d['data'], self.client) for d in data['children']]
