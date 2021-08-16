
from __future__ import annotations
from typing import Sequence

from .mixins.subreddit_detail_SYNC import SubredditDetail
from .listing_paginator import ListingPaginator
from ....models.load.subreddit_SYNC import load_subreddit
from ....models.subreddit_SYNC import Subreddit


class SubredditListingPaginator(ListingPaginator[Subreddit]):
    def fetch_next_result(self) -> Sequence[Subreddit]:
        data = self._fetch_data()
        return [load_subreddit(d['data'], self.client) for d in data['children']]


class UserSubredditListingPaginator(
    SubredditDetail[Subreddit],
    SubredditListingPaginator,
): pass
