
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.moderation_pull_sync import (
    ModQueueListingPaginator,
    ReportsListingPaginator,
    SpamListingPaginator,
    EditedListingPaginator,
    UnmoderatedListingPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def modqueue(self, sr: str, amount: Optional[int] = None, *, only: str = '',
            ) -> PaginatorChainingIterator[ModQueueListingPaginator, object]:
        p = ModQueueListingPaginator(self._client, f'/r/{sr}/about/modqueue')
        p.only = only
        return PaginatorChainingIterator(p, amount)

    def reports(self, sr: str, amount: Optional[int] = None, *, only: str = '',
            ) -> PaginatorChainingIterator[ReportsListingPaginator, object]:
        p = ReportsListingPaginator(self._client, f'/r/{sr}/about/reports')
        p.only = only
        return PaginatorChainingIterator(p, amount)

    def spam(self, sr: str, amount: Optional[int] = None, *, only: str = '',
            ) -> PaginatorChainingIterator[SpamListingPaginator, object]:
        p = SpamListingPaginator(self._client, f'/r/{sr}/about/spam')
        p.only = only
        return PaginatorChainingIterator(p, amount)

    def edited(self, sr: str, amount: Optional[int] = None, *, only: str = '',
            ) -> PaginatorChainingIterator[EditedListingPaginator, object]:
        p = EditedListingPaginator(self._client, f'/r/{sr}/about/edited')
        p.only = only
        return PaginatorChainingIterator(p, amount)

    def unmoderated(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[UnmoderatedListingPaginator, Submission]:
        p = UnmoderatedListingPaginator(self._client, f'/r/{sr}/about/unmoderated')
        return PaginatorChainingIterator(p, amount)
