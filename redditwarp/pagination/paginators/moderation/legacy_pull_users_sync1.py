
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence
if TYPE_CHECKING:
    from ....client_SYNC import Client

from operator import itemgetter

from ..listing.listing_paginator import ListingPaginator
from ....model_loaders.user_relationship import load_user_relationship, load_banned_subreddit_user_relation
from ....models.user_relationship import UserRelationship, BannedSubredditUserRelationship

T = TypeVar('T')

class LegacyModerationUsersPaginator(ListingPaginator[T]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 100,
    ) -> None:
        super().__init__(client, url, limit=limit, cursor_extractor=itemgetter('rel_id'))


class UserRelationshipListingPaginator(LegacyModerationUsersPaginator[UserRelationship]):
    def fetch(self) -> Sequence[UserRelationship]:
        data = self._fetch_data()
        return [load_user_relationship(d) for d in data['children']]

class BannedSubredditUserRelationshipListingPaginator(LegacyModerationUsersPaginator[BannedSubredditUserRelationship]):
    def fetch(self) -> Sequence[BannedSubredditUserRelationship]:
        data = self._fetch_data()
        return [load_banned_subreddit_user_relation(d) for d in data['children']]
