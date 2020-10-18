
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.comment_SYNC import Comment
    from ....models.submission_SYNC import Submission
    from ....models.original_reddit_thing_object import OriginalRedditThingObject

from ....iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ....iterators.paginators.listing.comment_listing_paginator import CommentListingPaginator
from ....iterators.paginators.listing.subreddit_detail_submission_listing_paginator import SubredditDetailSubmissionListingPaginator
from ....iterators.paginators.listing.subreddit_detail_comment_and_submission_listing_paginator import SubredditDetailCommentAndSubmissionListingPaginator

class Pull:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailCommentAndSubmissionListingPaginator, OriginalRedditThingObject]:
        return self.overview(name, amount)

    def overview(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailCommentAndSubmissionListingPaginator, OriginalRedditThingObject]:
        p = SubredditDetailCommentAndSubmissionListingPaginator(self._client, f'/user/{name}/overview')
        return PaginatorChainingIterator(p, amount)

    def submitted(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, f'/user/{name}/submitted')
        return PaginatorChainingIterator(p, amount)

    def comments(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[CommentListingPaginator, Comment]:
        p = CommentListingPaginator(self._client, f'/user/{name}/comments')
        return PaginatorChainingIterator(p, amount)

    def gilded(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailCommentAndSubmissionListingPaginator, OriginalRedditThingObject]:
        p = SubredditDetailCommentAndSubmissionListingPaginator(self._client, f'/user/{name}/gilded')
        return PaginatorChainingIterator(p, amount)

    def upvoted(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, f'/user/{name}/upvoted')
        return PaginatorChainingIterator(p, amount)

    def downvoted(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, f'/user/{name}/downvoted')
        return PaginatorChainingIterator(p, amount)

    def hidden(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, f'/user/{name}/hidden')
        return PaginatorChainingIterator(p, amount)

    def saved(self, name: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailCommentAndSubmissionListingPaginator, Submission]:
        p = SubredditDetailCommentAndSubmissionListingPaginator(self._client, f'/user/{name}/saved')
        return PaginatorChainingIterator(p, amount)
