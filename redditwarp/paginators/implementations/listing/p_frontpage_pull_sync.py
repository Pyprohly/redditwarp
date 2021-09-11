
from __future__ import annotations

from .mixins.time_filter_SYNC import TimeFilter
from .mixins.subreddit_detail_SYNC import SubredditDetail
from .p_user_pull_sync import SubmissionAndExtraSubmissionFieldsCommentListingPaginator
from .submission_listing_paginator_sync import SubmissionListingPaginator
from ....models.submission_SYNC import Submission

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
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class RisingListingPaginator(
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class ControversialListingPaginator(
    TimeFilter[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class GildedListingPaginator(
    TimeFilter[object],
    SubredditDetail[object],
    SubmissionAndExtraSubmissionFieldsCommentListingPaginator,
): pass
