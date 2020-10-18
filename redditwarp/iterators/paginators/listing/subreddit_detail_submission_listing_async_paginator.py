
from __future__ import annotations

from .subreddit_detail_listing_async_paginator import SubredditDetailListingAsyncPaginator
from .submission_listing_async_paginator import SubmissionListingAsyncPaginator
from ....models.submission_SYNC import Submission

class SubredditDetailSubmissionListingAsyncPaginator(
    SubredditDetailListingAsyncPaginator[Submission],
    SubmissionListingAsyncPaginator,
):
    pass
