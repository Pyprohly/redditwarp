
from __future__ import annotations

from .time_filter_listing_paginator import TimeFilterListingPaginator
from .submission_listing_paginator import SubmissionListingPaginator
from ....models.submission_SYNC import Submission

class TimeFilterSubmissionListingPaginator(
    TimeFilterListingPaginator[Submission],
    SubmissionListingPaginator,
):
    pass
