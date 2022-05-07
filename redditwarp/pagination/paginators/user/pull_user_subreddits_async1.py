
from __future__ import annotations

from ..listing.mixins.subreddit_detail_ASYNC import SubredditDetail
from ..listing.subreddit_listing_async_paginator import SubredditListingAsyncPaginator
from ....models.subreddit_ASYNC import Subreddit

class UserSubredditListingAsyncPaginator(
    SubredditDetail[Subreddit],
    SubredditListingAsyncPaginator,
): pass
