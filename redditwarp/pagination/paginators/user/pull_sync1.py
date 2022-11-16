
from __future__ import annotations
from typing import Iterable

from ..listing.mixins.sort_SYNC import Sort
from ..listing.mixins.subreddit_detail_SYNC import SubredditDetail
from ..listing.submission_listing_paginator import SubmissionListingPaginator
from ..listing.comment_listing_paginator import LooseCommentListingPaginator
from ..listing.submission_and_comment_listing_paginator import SubmissionAndLooseCommentListingPaginator
from ....models.comment_SYNC import LooseComment
from ....models.submission_SYNC import Submission

class OverviewListingPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass

class CommentsListingPaginator(
    Sort[LooseComment],
    SubredditDetail[LooseComment],
    LooseCommentListingPaginator,
): pass

class SubmittedListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class GildedListingPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass

class UpvotedListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class DownvotedListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class HiddenListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
): pass

class SavedListingPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingPaginator,
): pass

class SavedSubmissionsListingPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'links')

class SavedCommentsListingPaginator(
    Sort[LooseComment],
    SubredditDetail[LooseComment],
    LooseCommentListingPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'comments')
