
from __future__ import annotations

from .subreddit_detail_listing_paginator import SubredditDetailListingPaginator
from .comment_and_submission_listing_paginator import CommentAndSubmissionListingPaginator
from ....models.original_reddit_thing_object import OriginalRedditThingObject

class SubredditDetailCommentAndSubmissionListingPaginator(
    SubredditDetailListingPaginator[OriginalRedditThingObject],
    CommentAndSubmissionListingPaginator,
):
    pass
