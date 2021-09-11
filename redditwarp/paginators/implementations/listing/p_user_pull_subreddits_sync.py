
from __future__ import annotations

from .mixins.subreddit_detail_SYNC import SubredditDetail
from .subreddit_listing_paginator_sync import SubredditListingPaginator
from ....models.subreddit_SYNC import Subreddit

class UserSubredditListingPaginator(
    SubredditDetail[Subreddit],
    SubredditListingPaginator,
): pass
