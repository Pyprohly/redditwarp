
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_relationship_item import (
        UserRelationshipItem,
        BannedUserRelationshipItem,
    )

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_subreddit_legacy_pull_users_sync import (
    UserRelationshipItemListingPaginator,
    BannedUserRelationshipItemListingPaginator,
)

class LegacyPullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def contributors(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/contributors')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def wiki_contributors(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikicontributors')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def banned(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/banned')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def muted(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/muted')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def wiki_banned(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingWrapper[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikibanned')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
