
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.front_sync1 import (
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

    def hot(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[HotListingPaginator, Submission]:
        p = HotListingPaginator(self._client, f'/r/{sr}/hot')
        return ImpartedPaginatorChainingIterator(p, amount)

    def top(self, sr: str, amount: Optional[int] = None, *,
            time: str = '',
            ) -> ImpartedPaginatorChainingIterator[TopListingPaginator, Submission]:
        p = TopListingPaginator(self._client, f'/r/{sr}/top')
        p.time = time
        return ImpartedPaginatorChainingIterator(p, amount)

    def new(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[NewListingPaginator, Submission]:
        p = NewListingPaginator(self._client, f'/r/{sr}/new')
        return ImpartedPaginatorChainingIterator(p, amount)

    def rising(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[RisingListingPaginator, Submission]:
        p = RisingListingPaginator(self._client, f'/r/{sr}/rising')
        return ImpartedPaginatorChainingIterator(p, amount)

    def controversial(self, sr: str, amount: Optional[int] = None, *,
            time: str = '',
            ) -> ImpartedPaginatorChainingIterator[ControversialListingPaginator, Submission]:
        p = ControversialListingPaginator(self._client, f'/r/{sr}/controversial')
        p.time = time
        return ImpartedPaginatorChainingIterator(p, amount)

    def gilded(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[GildedListingPaginator, object]:
        p = GildedListingPaginator(self._client, f'/r/{sr}/gilded')
        return ImpartedPaginatorChainingIterator(p, amount)
