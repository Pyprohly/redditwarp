
from __future__ import annotations

from ..listing.mixins.subreddit_detail_SYNC import SubredditDetail
from ..listing.subreddit_listing_paginator_sync import SubredditListingPaginator
from ...models.subreddit_SYNC import Subreddit

class SubscribedListingPaginator(
    SubredditDetail[Subreddit],
    SubredditListingPaginator,
): pass

class ContributingListingPaginator(
    SubredditDetail[Subreddit],
    SubredditListingPaginator,
): pass

class ModeratingListingPaginator(
    SubredditDetail[Subreddit],
    SubredditListingPaginator,
): pass
