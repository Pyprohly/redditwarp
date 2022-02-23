
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.implementations.front_async import (
    BestListingAsyncPaginator,
    HotListingAsyncPaginator,
    NewListingAsyncPaginator,
    TopListingAsyncPaginator,
    RisingListingAsyncPaginator,
    ControversialListingAsyncPaginator,
    GildedListingAsyncPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def best(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[BestListingAsyncPaginator, Submission]:
        p = BestListingAsyncPaginator(self._client, '/best')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def hot(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[HotListingAsyncPaginator, Submission]:
        p = HotListingAsyncPaginator(self._client, '/hot')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def new(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[NewListingAsyncPaginator, Submission]:
        p = NewListingAsyncPaginator(self._client, '/new')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def top(self, amount: Optional[int] = None, *,
            time: str = 'day',
            ) -> ImpartedPaginatorChainingAsyncIterator[TopListingAsyncPaginator, Submission]:
        p = TopListingAsyncPaginator(self._client, '/top')
        p.time = time
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def rising(self, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[RisingListingAsyncPaginator, Submission]:
        p = RisingListingAsyncPaginator(self._client, '/rising')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def controversial(self, amount: Optional[int] = None, *,
            time: str = 'day',
        ) -> ImpartedPaginatorChainingAsyncIterator[ControversialListingAsyncPaginator, Submission]:
        p = ControversialListingAsyncPaginator(self._client, '/controversial')
        p.time = time
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def gilded(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[GildedListingAsyncPaginator, object]:
        p = GildedListingAsyncPaginator(self._client, '/gilded')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
