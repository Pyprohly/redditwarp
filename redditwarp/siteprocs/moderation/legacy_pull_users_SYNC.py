
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_relationship_item import (
        UserRelationshipItem,
        BannedUserRelationshipItem,
    )

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.subreddit_legacy_pull_users_sync import (
    UserRelationshipItemListingPaginator,
    BannedUserRelationshipItemListingPaginator,
)

class LegacyPullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def contributors(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/contributors')
        return PaginatorChainingIterator(p, amount)

    def wiki_contributors(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikicontributors')
        return PaginatorChainingIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/banned')
        return PaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/muted')
        return PaginatorChainingIterator(p, amount)

    def wiki_banned(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikibanned')
        return PaginatorChainingIterator(p, amount)
