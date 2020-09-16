
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.submission import Submission

from ....iterators.paginators.page_chaining_iterator import PaginatorKeepingPageChainingIterator
from ....iterators.paginators.listing.submission_listing_paginator import SubmissionListingPaginator
from ....iterators.paginators.listing.time_filter_submission_listing_paginator import TimeFilterSubmissionListingPaginator

class pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, sr: str, sort: str, amount: Optional[int] = None) -> PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, Submission]:
        #if sort not in 'hot best rising top new controversial gilded':
        #    raise ValueError(f"'{sort}' is not a valid sort option")
        return self._get_itr(f'/r/{sr}/{sort}', amount)

    def _get_itr(self, uri: str, amount: Optional[int] = None) -> PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, Submission]:
        p = SubmissionListingPaginator(self._client, uri)
        p.limit = 100
        return PaginatorKeepingPageChainingIterator(p, amount)

    def hot(self, sr: str, amount: Optional[int] = None) -> PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, Submission]:
        return self._get_itr(f'/r/{sr}/hot', amount)

    # best works but it is the same as hot for subreddit listings
    '''
    def best(self, sr: str, amount: Optional[int] = None) -> PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, Submission]:
        return self._get_itr(f'/r/{sr}/best', amount)
    '''#'''

    def rising(self, sr: str, amount: Optional[int] = None) -> PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, Submission]:
        return self._get_itr(f'/r/{sr}/rising', amount)

    def top(self,
        sr: str,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorKeepingPageChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, f'/r/{sr}/top')
        p.limit = 100
        p.time_filter = time_filter
        return PaginatorKeepingPageChainingIterator(p, amount)

    def new(self, sr: str, amount: Optional[int] = None) -> PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, Submission]:
        return self._get_itr(f'/r/{sr}/new', amount)

    def controversial(self,
        sr: str,
        amount: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> PaginatorKeepingPageChainingIterator[TimeFilterSubmissionListingPaginator, Submission]:
        p = TimeFilterSubmissionListingPaginator(self._client, f'/r/{sr}/controversial')
        p.limit = 100
        p.time_filter = time_filter
        return PaginatorKeepingPageChainingIterator(p, amount)

    # TODO: make return type PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, (super class of submission and comment)]
    def gilded(self, sr: str, amount: Optional[int] = None) -> PaginatorKeepingPageChainingIterator[SubmissionListingPaginator, Submission]:
        return self._get_itr(f'/r/{sr}/gilded', amount)
