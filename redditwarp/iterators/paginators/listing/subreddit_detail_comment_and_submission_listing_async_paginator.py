
from __future__ import annotations

from .subreddit_detail_listing_async_paginator import SubredditDetailListingAsyncPaginator
from .comment_and_submission_listing_async_paginator import CommentAndSubmissionListingAsyncPaginator

class SubredditDetailCommentAndSubmissionListingAsyncPaginator(
    SubredditDetailListingAsyncPaginator[object],
    CommentAndSubmissionListingAsyncPaginator,
):
    pass
