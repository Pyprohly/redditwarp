
from __future__ import annotations

from .listing.mixins.subreddit_detail_SYNC import SubredditDetail
from .listing.submission_listing_paginator import SubmissionListingPaginator
from ...models.submission_SYNC import Submission
from .listing.mixins.time_SYNC import Time
from .listing.submission_and_comment_listing_paginator import SubmissionAndLooseCommentListingPaginator

class BestListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class HotListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class NewListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class TopListingPaginator(
    Time[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class RisingListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class ControversialListingPaginator(
    Time[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class GildedListingPaginator(
    Time[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass
