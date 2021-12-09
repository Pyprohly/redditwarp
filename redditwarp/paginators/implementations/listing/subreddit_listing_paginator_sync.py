
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.load.subreddit_SYNC import load_subreddit
from ....models.subreddit_SYNC import Subreddit

class SubredditListingPaginator(ListingPaginator[Subreddit]):
    def fetch_next(self) -> Sequence[Subreddit]:
        data = self._next_data()
        return [load_subreddit(d['data'], self.client) for d in data['children']]
