
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ...models.load.user_relationship_item import load_user_relationship_item, load_banned_user_relation_item
from ...models.user_relationship_item import UserRelationshipItem, BannedUserRelationshipItem

class UserRelationshipItemListingPaginator(ListingPaginator[UserRelationshipItem]):
    def _fetch_result(self) -> Sequence[UserRelationshipItem]:
        data = self._fetch_data()
        return [load_user_relationship_item(d) for d in data['children']]

class BannedUserRelationshipItemListingPaginator(ListingPaginator[BannedUserRelationshipItem]):
    def _fetch_result(self) -> Sequence[BannedUserRelationshipItem]:
        data = self._fetch_data()
        return [load_banned_user_relation_item(d) for d in data['children']]
