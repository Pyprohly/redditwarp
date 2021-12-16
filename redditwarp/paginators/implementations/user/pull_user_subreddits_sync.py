
from __future__ import annotations

from ...listing.mixins.subreddit_detail_SYNC import SubredditDetail
from ...listing.subreddit_listing_paginator_sync import SubredditListingPaginator
from ....models.subreddit_SYNC import Subreddit

class UserSubredditListingPaginator(
    SubredditDetail[Subreddit],
    SubredditListingPaginator,
): pass
