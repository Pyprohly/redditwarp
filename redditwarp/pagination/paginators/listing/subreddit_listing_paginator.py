
from __future__ import annotations
from typing import Sequence

from ..listing.listing_paginator import ListingPaginator
from ....model_loaders.subreddit_SYNC import load_subreddit
from ....models.subreddit_SYNC import Subreddit

class SubredditListingPaginator(ListingPaginator[Subreddit]):
    def fetch(self) -> Sequence[Subreddit]:
        data = self._fetch_data()
        return [load_subreddit(d['data'], self.client) for d in data['children']]
