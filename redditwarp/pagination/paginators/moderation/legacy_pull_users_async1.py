
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from operator import itemgetter

from ..listing.listing_async_paginator import ListingAsyncPaginator
from ....model_loaders.user_relationship_item import load_user_relationship_item, load_banned_user_relation_item
from ....models.user_relationship_item import UserRelationshipItem, BannedUserRelationshipItem

T = TypeVar('T')

class LegacyModerationUsersAsyncPaginator(ListingAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=itemgetter('rel_id'))


class UserRelationshipItemListingAsyncPaginator(LegacyModerationUsersAsyncPaginator[UserRelationshipItem]):
    async def fetch(self) -> Sequence[UserRelationshipItem]:
        data = await self._fetch_data()
        return [load_user_relationship_item(d) for d in data['children']]

class BannedUserRelationshipItemListingAsyncPaginator(LegacyModerationUsersAsyncPaginator[BannedUserRelationshipItem]):
    async def fetch(self) -> Sequence[BannedUserRelationshipItem]:
        data = await self._fetch_data()
        return [load_banned_user_relation_item(d) for d in data['children']]
