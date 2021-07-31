
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.submission_SYNC import Submission

from .mixins.time_filter_SYNC import TimeFilter
from .mixins.subreddit_detail_SYNC import SubredditDetail
from .user_pull_sync import SubmissionListingPaginator

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
