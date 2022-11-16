
from __future__ import annotations

from .listing.mixins.subreddit_detail_ASYNC import SubredditDetail
from .listing.submission_listing_async_paginator import SubmissionListingAsyncPaginator
from ...models.submission_ASYNC import Submission
from .listing.mixins.time_ASYNC import Time
from .listing.submission_and_comment_listing_async_paginator import SubmissionAndLooseCommentListingAsyncPaginator

class BestListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class HotListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class NewListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class TopListingAsyncPaginator(
    Time[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class RisingListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class ControversialListingAsyncPaginator(
    Time[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class GildedListingAsyncPaginator(
    Time[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingAsyncPaginator,
): pass
