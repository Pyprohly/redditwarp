
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.submission_SYNC import Submission
    from ....models.original_reddit_thing_object import OriginalRedditThingObject

from ....iterators.paginators.page_chaining_iterator import PaginatorPageChainingIterator
from ....iterators.paginators.listing.submission_listing_paginator import SubmissionListingPaginator
from ....iterators.paginators.listing.comment_and_submission_listing_paginator import CommentAndSubmissionListingPaginator
from ....iterators.paginators.listing.time_filter_submission_listing_paginator import TimeFilterSubmissionListingPaginator

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, sort: str, amount: Optional[int] = None) -> PaginatorPageChainingIterator[SubmissionListingPaginator, Submission]:
        p = SubmissionListingPaginator(self._client, f'/{sort}')
        p.limit = 100
        return PaginatorPageChainingIterator(p, amount)

    def best(self, amount: Optional[int] = None) -> PaginatorPageChainingIterator[SubmissionListingPaginator, Submission]:
        p = SubmissionListingPaginator(self._client, '/best')
        p.limit = 100
        return PaginatorPageChainingIterator(p, amount)

    def hot(self, amount: Optional[int] = None) -> PaginatorPageChainingIterator[SubmissionListingPaginator, Submission]:
        p = SubmissionListingPaginator(self._client, '/hot')
        p.limit = 100
        return PaginatorPageChainingIterator(p, amount)

    def rising(self, amount: Optional[int] = None) -> PaginatorPageChainingIterator[SubmissionListingPaginator, Submission]:
        p = SubmissionListingPaginator(self._client, '/rising')
        p.limit = 100
        return PaginatorPageChainingIterator(p, amount)

    def top(self,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorPageChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, '/top')
        p.limit = 100
        p.time_filter = time_filter
        return PaginatorPageChainingIterator(p, amount)

    def new(self, amount: Optional[int] = None) -> PaginatorPageChainingIterator[SubmissionListingPaginator, Submission]:
        p = SubmissionListingPaginator(self._client, '/new')
        p.limit = 100
        return PaginatorPageChainingIterator(p, amount)

    def controversial(self,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorPageChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, '/controversial')
        p.limit = 100
        p.time_filter = time_filter
        return PaginatorPageChainingIterator(p, amount)

    def gilded(self, amount: Optional[int] = None) -> PaginatorPageChainingIterator[CommentAndSubmissionListingPaginator, OriginalRedditThingObject]:
        p = CommentAndSubmissionListingPaginator(self._client, '/gilded')
        p.limit = 100
        return PaginatorPageChainingIterator(p, amount)
