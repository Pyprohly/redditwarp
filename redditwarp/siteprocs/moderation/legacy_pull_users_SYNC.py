
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_relationship import (
        UserRelationship,
        BannedSubredditUserRelationship,
    )

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.moderation.sync1 import (
    UserRelationshipListingPaginator,
    BannedSubredditUserRelationshipListingPaginator,
)

class LegacyPullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def approved_users(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UserRelationshipListingPaginator, UserRelationship]:
        p = UserRelationshipListingPaginator(self._client, f'/r/{sr}/about/contributors')
        return ImpartedPaginatorChainingIterator(p, amount)

    def wiki_contributors(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UserRelationshipListingPaginator, UserRelationship]:
        p = UserRelationshipListingPaginator(self._client, f'/r/{sr}/about/wikicontributors')
        return ImpartedPaginatorChainingIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[BannedSubredditUserRelationshipListingPaginator, BannedSubredditUserRelationship]:
        p = BannedSubredditUserRelationshipListingPaginator(self._client, f'/r/{sr}/about/banned')
        return ImpartedPaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UserRelationshipListingPaginator, UserRelationship]:
        p = UserRelationshipListingPaginator(self._client, f'/r/{sr}/about/muted')
        return ImpartedPaginatorChainingIterator(p, amount)

    def wiki_banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[BannedSubredditUserRelationshipListingPaginator, BannedSubredditUserRelationship]:
        p = BannedSubredditUserRelationshipListingPaginator(self._client, f'/r/{sr}/about/wikibanned')
        return ImpartedPaginatorChainingIterator(p, amount)
