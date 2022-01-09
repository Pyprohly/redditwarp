
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.user_relationship_item import (
        UserRelationshipItem,
        BannedUserRelationshipItem,
    )

from ...paginators.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...paginators.implementations.moderation._async_ import (
    UserRelationshipItemListingAsyncPaginator,
    BannedUserRelationshipItemListingAsyncPaginator,
)

class LegacyPullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def contributors(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UserRelationshipItemListingAsyncPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingAsyncPaginator(self._client, f'/r/{sr}/about/contributors')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def wiki_contributors(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UserRelationshipItemListingAsyncPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingAsyncPaginator(self._client, f'/r/{sr}/about/wikicontributors')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[BannedUserRelationshipItemListingAsyncPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingAsyncPaginator(self._client, f'/r/{sr}/about/banned')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UserRelationshipItemListingAsyncPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingAsyncPaginator(self._client, f'/r/{sr}/about/muted')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def wiki_banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[BannedUserRelationshipItemListingAsyncPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingAsyncPaginator(self._client, f'/r/{sr}/about/wikibanned')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
