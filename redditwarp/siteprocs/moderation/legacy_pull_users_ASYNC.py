
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.user_relationship import (
        UserRelationship,
        BannedSubredditUserRelationship,
    )

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.moderation.async1 import (
    UserRelationshipListingAsyncPaginator,
    BannedSubredditUserRelationshipListingAsyncPaginator,
)

class LegacyPullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def approved_users(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UserRelationshipListingAsyncPaginator, UserRelationship]:
        p = UserRelationshipListingAsyncPaginator(self._client, f'/r/{sr}/about/contributors')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def wiki_contributors(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UserRelationshipListingAsyncPaginator, UserRelationship]:
        p = UserRelationshipListingAsyncPaginator(self._client, f'/r/{sr}/about/wikicontributors')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[BannedSubredditUserRelationshipListingAsyncPaginator, BannedSubredditUserRelationship]:
        p = BannedSubredditUserRelationshipListingAsyncPaginator(self._client, f'/r/{sr}/about/banned')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UserRelationshipListingAsyncPaginator, UserRelationship]:
        p = UserRelationshipListingAsyncPaginator(self._client, f'/r/{sr}/about/muted')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def wiki_banned(self, sr: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[BannedSubredditUserRelationshipListingAsyncPaginator, BannedSubredditUserRelationship]:
        p = BannedSubredditUserRelationshipListingAsyncPaginator(self._client, f'/r/{sr}/about/wikibanned')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
