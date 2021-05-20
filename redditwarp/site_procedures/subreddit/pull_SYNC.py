
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission
    from ...models.original_reddit_thing_object import OriginalRedditThingObject

from ...iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...iterators.paginators.listing.subreddit_detail_submission_listing_paginator import SubredditDetailSubmissionListingPaginator
from ...iterators.paginators.listing.subreddit_detail_comment_and_submission_listing_paginator import SubredditDetailCommentAndSubmissionListingPaginator
from ...iterators.paginators.listing.time_filter_submission_listing_paginator import TimeFilterSubmissionListingPaginator

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        return self.new(sr, amount)

    def hot(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, f'/r/{sr}/hot')
        return PaginatorChainingIterator(p, amount)

    def rising(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, f'/r/{sr}/rising')
        return PaginatorChainingIterator(p, amount)

    def top(self,
        sr: str,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, f'/r/{sr}/top')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def new(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, f'/r/{sr}/new')
        return PaginatorChainingIterator(p, amount)

    def controversial(self,
        sr: str,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, f'/r/{sr}/controversial')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def gilded(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailCommentAndSubmissionListingPaginator, OriginalRedditThingObject]:
        p = SubredditDetailCommentAndSubmissionListingPaginator(self._client, f'/r/{sr}/gilded')
        return PaginatorChainingIterator(p, amount)
