
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.implementations.front_async import (
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

    def hot(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[HotListingAsyncPaginator, Submission]:
        p = HotListingAsyncPaginator(self._client, f'/r/{sr}/hot')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def top(self, sr: str, amount: Optional[int] = None, *,
            time: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[TopListingAsyncPaginator, Submission]:
        p = TopListingAsyncPaginator(self._client, f'/r/{sr}/top')
        p.time = time
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def new(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[NewListingAsyncPaginator, Submission]:
        p = NewListingAsyncPaginator(self._client, f'/r/{sr}/new')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def rising(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[RisingListingAsyncPaginator, Submission]:
        p = RisingListingAsyncPaginator(self._client, f'/r/{sr}/rising')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def controversial(self, sr: str, amount: Optional[int] = None, *,
            time: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ControversialListingAsyncPaginator, Submission]:
        p = ControversialListingAsyncPaginator(self._client, f'/r/{sr}/controversial')
        p.time = time
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def gilded(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[GildedListingAsyncPaginator, object]:
        p = GildedListingAsyncPaginator(self._client, f'/r/{sr}/gilded')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
