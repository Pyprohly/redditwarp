
from __future__ import annotations

from .subreddit_detail_listing_paginator import SubredditDetailListingPaginator
from .submission_listing_paginator import SubmissionListingPaginator
from ....models.submission_SYNC import Submission

class SubredditDetailSubmissionListingPaginator(
    SubredditDetailListingPaginator[Submission],
    SubmissionListingPaginator,
):
    pass
