
from __future__ import annotations

from ..listing.mixins.subreddit_detail_ASYNC import SubredditDetail
from ..listing.submission_listing_async_paginator import SubmissionListingAsyncPaginator
from ...models.submission_ASYNC import Submission
from ..listing.mixins.time_filter_ASYNC import TimeFilter
from ..listing.submission_and_comment_listing_async_paginator import SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator

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
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class RisingListingAsyncPaginator(
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class ControversialListingAsyncPaginator(
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class GildedListingAsyncPaginator(
    TimeFilter[object],
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingAsyncPaginator,
): pass
