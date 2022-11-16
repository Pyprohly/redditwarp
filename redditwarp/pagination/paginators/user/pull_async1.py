
from __future__ import annotations
from typing import Iterable

from ..listing.mixins.sort_ASYNC import Sort
from ..listing.mixins.subreddit_detail_ASYNC import SubredditDetail
from ..listing.submission_listing_async_paginator import SubmissionListingAsyncPaginator
from ..listing.comment_listing_async_paginator import LooseCommentListingAsyncPaginator
from ..listing.submission_and_comment_listing_async_paginator import SubmissionAndLooseCommentListingAsyncPaginator
from ....models.comment_ASYNC import LooseComment
from ....models.submission_ASYNC import Submission

class OverviewListingAsyncPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingAsyncPaginator,
): pass

class CommentsListingAsyncPaginator(
    Sort[LooseComment],
    SubredditDetail[LooseComment],
    LooseCommentListingAsyncPaginator,
): pass

class SubmittedListingAsyncPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class GildedListingAsyncPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingAsyncPaginator,
): pass

class UpvotedListingAsyncPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class DownvotedListingAsyncPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class HiddenListingAsyncPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
): pass

class SavedListingAsyncPaginator(
    Sort[object],
    SubredditDetail[object],
    SubmissionAndLooseCommentListingAsyncPaginator,
): pass

class SavedSubmissionsListingAsyncPaginator(
    Sort[Submission],
    SubredditDetail[Submission],
    SubmissionListingAsyncPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'links')

class SavedCommentsListingAsyncPaginator(
    Sort[LooseComment],
    SubredditDetail[LooseComment],
    LooseCommentListingAsyncPaginator,
):
    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        yield ('type', 'comments')
