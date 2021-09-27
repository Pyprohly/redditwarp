
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
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
            ) -> PaginatorChainingWrapper[BestListingPaginator, Submission]:
        return self.best(amount)

    def best(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[BestListingPaginator, Submission]:
        p = BestListingPaginator(self._client, '/best')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def hot(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[HotListingPaginator, Submission]:
        p = HotListingPaginator(self._client, '/hot')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def new(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[NewListingPaginator, Submission]:
        p = NewListingPaginator(self._client, '/new')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def top(self, amount: Optional[int] = None, *,
            time_filter: str = 'day',
            ) -> PaginatorChainingWrapper[TopListingPaginator, Submission]:
        p = TopListingPaginator(self._client, '/top')
        p.time_filter = time_filter
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def rising(self, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[RisingListingPaginator, Submission]:
        p = RisingListingPaginator(self._client, '/rising')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def controversial(self, amount: Optional[int] = None, *,
            time_filter: str = 'day',
        ) -> PaginatorChainingWrapper[ControversialListingPaginator, Submission]:
        p = ControversialListingPaginator(self._client, '/controversial')
        p.time_filter = time_filter
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def gilded(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, '/gilded')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
