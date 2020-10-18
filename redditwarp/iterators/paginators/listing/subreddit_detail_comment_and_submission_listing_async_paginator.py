
from __future__ import annotations

from .subreddit_detail_listing_async_paginator import SubredditDetailListingAsyncPaginator
from .comment_and_submission_listing_async_paginator import CommentAndSubmissionListingAsyncPaginator
from ....models.original_reddit_thing_object import OriginalRedditThingObject

class SubredditDetailCommentAndSubmissionListingAsyncPaginator(
    SubredditDetailListingAsyncPaginator[OriginalRedditThingObject],
    CommentAndSubmissionListingAsyncPaginator,
):
    pass
