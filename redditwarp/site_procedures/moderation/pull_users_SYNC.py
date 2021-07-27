
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_relationship_item import (
        UserRelationshipItem,
        BannedUserRelationshipItem,
    )

from operator import itemgetter

from ...iterators.paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...iterators.paginators.listing.subreddit_pull_users_sync import (
    UserRelationshipItemListingPaginator,
    BannedUserRelationshipItemListingPaginator,
)

class PullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def banned(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/banned', cursor_extractor=itemgetter('rel_id'))
        return PaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/muted', cursor_extractor=itemgetter('rel_id'))
        return PaginatorChainingIterator(p, amount)

    def contributors(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/contributors', cursor_extractor=itemgetter('rel_id'))
        return PaginatorChainingIterator(p, amount)

    def wiki_banned(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[BannedUserRelationshipItemListingPaginator, BannedUserRelationshipItem]:
        p = BannedUserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikibanned', cursor_extractor=itemgetter('rel_id'))
        return PaginatorChainingIterator(p, amount)

    def wiki_contributors(self, sr: str, amount: Optional[int] = None,
            ) -> PaginatorChainingIterator[UserRelationshipItemListingPaginator, UserRelationshipItem]:
        p = UserRelationshipItemListingPaginator(self._client, f'/r/{sr}/about/wikicontributors', cursor_extractor=itemgetter('rel_id'))
        return PaginatorChainingIterator(p, amount)
