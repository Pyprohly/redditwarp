
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission

from ...paginators.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...paginators.implementations.front_sync import (
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
            ) -> ImpartedPaginatorChainingIterator[BestListingPaginator, Submission]:
        return self.best(amount)

    def best(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[BestListingPaginator, Submission]:
        p = BestListingPaginator(self._client, '/best')
        return ImpartedPaginatorChainingIterator(p, amount)

    def hot(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[HotListingPaginator, Submission]:
        p = HotListingPaginator(self._client, '/hot')
        return ImpartedPaginatorChainingIterator(p, amount)

    def new(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[NewListingPaginator, Submission]:
        p = NewListingPaginator(self._client, '/new')
        return ImpartedPaginatorChainingIterator(p, amount)

    def top(self, amount: Optional[int] = None, *,
            time_filter: str = 'day',
            ) -> ImpartedPaginatorChainingIterator[TopListingPaginator, Submission]:
        p = TopListingPaginator(self._client, '/top')
        p.time_filter = time_filter
        return ImpartedPaginatorChainingIterator(p, amount)

    def rising(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[RisingListingPaginator, Submission]:
        p = RisingListingPaginator(self._client, '/rising')
        return ImpartedPaginatorChainingIterator(p, amount)

    def controversial(self, amount: Optional[int] = None, *,
            time_filter: str = 'day',
        ) -> ImpartedPaginatorChainingIterator[ControversialListingPaginator, Submission]:
        p = ControversialListingPaginator(self._client, '/controversial')
        p.time_filter = time_filter
        return ImpartedPaginatorChainingIterator(p, amount)

    def gilded(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, '/gilded')
        return ImpartedPaginatorChainingIterator(p, amount)
