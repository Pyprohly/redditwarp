
from __future__ import annotations

from .time_filter_listing_async_paginator import TimeFilterListingAsyncPaginator
from .submission_listing_async_paginator import SubmissionListingAsyncPaginator
from ....models.submission_SYNC import Submission

class TimeFilterSubmissionListingAsyncPaginator(
    TimeFilterListingAsyncPaginator[Submission],
    SubmissionListingAsyncPaginator,
):
    pass
