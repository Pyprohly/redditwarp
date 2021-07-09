
from __future__ import annotations

from .subreddit_detail_listing_paginator import SubredditDetailListingPaginator
from .comment_and_submission_listing_paginator import CommentAndSubmissionListingPaginator

class SubredditDetailCommentAndSubmissionListingPaginator(
    SubredditDetailListingPaginator[object],
    CommentAndSubmissionListingPaginator,
):
    pass
