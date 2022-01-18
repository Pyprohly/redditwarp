
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_relationship_item import (
        UserRelationshipItem,
        BannedUserRelationshipItem,
    )

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.implementations.moderation._sync_ import (
    UserRelationshipItemListingPaginator,
    BannedUserRelationshipItemListingPaginator,
)

class LegacyPullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def contributors(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/contributors')
        return ImpartedPaginatorChainingIterator(p, amount)

    def wiki_contributors(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikicontributors')
        return ImpartedPaginatorChainingIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/banned')
        return ImpartedPaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/muted')
        return ImpartedPaginatorChainingIterator(p, amount)

    def wiki_banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikibanned')
        return ImpartedPaginatorChainingIterator(p, amount)
