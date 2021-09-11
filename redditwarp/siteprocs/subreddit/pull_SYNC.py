
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.p_frontpage_pull_sync import (
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

    def __call__(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[HotListingPaginator, Submission]:
        return self.hot(sr, amount)

    def hot(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[HotListingPaginator, Submission]:
        p = HotListingPaginator(self._client, f'/r/{sr}/hot')
        return PaginatorChainingIterator(p, amount)

    def top(self, sr: str, amount: Optional[int] = None, *,
            time_filter: str = '',
            ) -> PaginatorChainingIterator[TopListingPaginator, Submission]:
        p = TopListingPaginator(self._client, f'/r/{sr}/top')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def new(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[NewListingPaginator, Submission]:
        p = NewListingPaginator(self._client, f'/r/{sr}/new')
        return PaginatorChainingIterator(p, amount)

    def rising(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[RisingListingPaginator, Submission]:
        p = RisingListingPaginator(self._client, f'/r/{sr}/rising')
        return PaginatorChainingIterator(p, amount)

    def controversial(self, sr: str, amount: Optional[int] = None, *,
            time_filter: str = '',
            ) -> PaginatorChainingIterator[ControversialListingPaginator, Submission]:
        p = ControversialListingPaginator(self._client, f'/r/{sr}/controversial')
        p.time_filter = time_filter
        return PaginatorChainingIterator(p, amount)

    def gilded(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/r/{sr}/gilded')
        return PaginatorChainingIterator(p, amount)
