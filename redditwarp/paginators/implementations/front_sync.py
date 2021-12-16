
from __future__ import annotations

from ..listing.mixins.subreddit_detail_SYNC import SubredditDetail
from ..listing.submission_listing_paginator_sync import SubmissionListingPaginator
from ...models.submission_SYNC import Submission
from ..listing.mixins.time_filter_SYNC import TimeFilter
from ..listing.submission_and_comment_listing_paginator_sync import SubmissionAndExtraSubmissionFieldsCommentListingPaginator

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
