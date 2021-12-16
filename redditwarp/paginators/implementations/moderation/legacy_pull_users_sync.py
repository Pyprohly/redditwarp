
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence
if TYPE_CHECKING:
    from ....client_SYNC import Client

from operator import itemgetter

from ...listing.listing_paginator import ListingPaginator
from ....models.load.user_relationship_item import load_user_relationship_item, load_banned_user_relation_item
from ....models.user_relationship_item import UserRelationshipItem, BannedUserRelationshipItem

T = TypeVar('T')

class LegacyModerationUsersPaginator(ListingPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=itemgetter('rel_id'))


class UserRelationshipItemListingPaginator(LegacyModerationUsersPaginator[UserRelationshipItem]):
    def fetch_next(self) -> Sequence[UserRelationshipItem]:
        data = self._fetch_next_data()
        return [load_user_relationship_item(d) for d in data['children']]

class BannedUserRelationshipItemListingPaginator(LegacyModerationUsersPaginator[BannedUserRelationshipItem]):
    def fetch_next(self) -> Sequence[BannedUserRelationshipItem]:
        data = self._fetch_next_data()
        return [load_banned_user_relation_item(d) for d in data['children']]
