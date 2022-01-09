
from __future__ import annotations

from ..listing.mixins.subreddit_detail_ASYNC import SubredditDetail
from ..listing.subreddit_listing_async_paginator import SubredditListingAsyncPaginator
from ...models.subreddit_ASYNC import Subreddit

class SubscribedListingAsyncPaginator(
    SubredditDetail[Subreddit],
    SubredditListingAsyncPaginator,
): pass

class ContributingListingAsyncPaginator(
    SubredditDetail[Subreddit],
    SubredditListingAsyncPaginator,
): pass

class ModeratingListingAsyncPaginator(
    SubredditDetail[Subreddit],
    SubredditListingAsyncPaginator,
): pass
