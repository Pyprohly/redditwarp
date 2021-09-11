
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.p_frontpage_pull_sync import (
    BestListingPaginator,
    HotListingPaginator,
    NewListingPaginator,
    TopListingPaginator,
    RisingListingPaginator,
    ControversialListingPaginator,
    GildedListingPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[BestListingPaginator, Submission]:
        return self.best(amount)

    def best(self, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[BestListingPaginator, Submission]:
        p = BestListingPaginator(self._client, '/best')
        return PaginatorChainingIterator(p, amount)

    def hot(self, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[HotListingPaginator, Submission]:
        p = HotListingPaginator(self._client, '/hot')
        return PaginatorChainingIterator(p, amount)

    def new(self, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[NewListingPaginator, Submission]:
        p = NewListingPaginator(self._client, '/new')
        return PaginatorChainingIterator(p, amount)

    def top(self, amount: Optional[int] = None, *,
            time_filter: str = 'day',
            ) -> PaginatorChainingIterator[TopListingPaginator, Submission]:
        p = TopListingPaginator(self._client, '/top')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def rising(self, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[RisingListingPaginator, Submission]:
        p = RisingListingPaginator(self._client, '/rising')
        return PaginatorChainingIterator(p, amount)

    def controversial(self, amount: Optional[int] = None, *,
            time_filter: str = 'day',
        ) -> PaginatorChainingIterator[ControversialListingPaginator, Submission]:
        p = ControversialListingPaginator(self._client, '/controversial')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def gilded(self, amount: Optional[int] = None) -> PaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, '/gilded')
        return PaginatorChainingIterator(p, amount)
