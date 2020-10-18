
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.submission_SYNC import Submission
    from ....models.original_reddit_thing_object import OriginalRedditThingObject

from ....iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ....iterators.paginators.listing.subreddit_detail_submission_listing_paginator import SubredditDetailSubmissionListingPaginator
from ....iterators.paginators.listing.subreddit_detail_comment_and_submission_listing_paginator import SubredditDetailCommentAndSubmissionListingPaginator
from ....iterators.paginators.listing.time_filter_submission_listing_paginator import TimeFilterSubmissionListingPaginator

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        return self.new(amount)

    def best(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, '/best')
        return PaginatorChainingIterator(p, amount)

    def hot(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, '/hot')
        return PaginatorChainingIterator(p, amount)

    def rising(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, '/rising')
        return PaginatorChainingIterator(p, amount)

    def top(self,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, '/top')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def new(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailSubmissionListingPaginator, Submission]:
        p = SubredditDetailSubmissionListingPaginator(self._client, '/new')
        return PaginatorChainingIterator(p, amount)

    def controversial(self,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, '/controversial')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def gilded(self, amount: Optional[int] = None) -> PaginatorChainingIterator[SubredditDetailCommentAndSubmissionListingPaginator, OriginalRedditThingObject]:
        p = SubredditDetailCommentAndSubmissionListingPaginator(self._client, '/gilded')
        return PaginatorChainingIterator(p, amount)
