
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.user_relationship_item import (
        UserRelationshipItem,
        BannedUserRelationshipItem,
    )
    from ...models.moderator_list import ModeratorListItem

from ...model_loaders.moderator_list import load_moderator_list_item
from ...model_loaders.user_relationship_item import load_user_relationship_item, load_banned_user_relation_item

from .legacy_pull_users_ASYNC import LegacyPullUsers

class Legacy:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull_users: LegacyPullUsers = LegacyPullUsers(client)

    async def list_moderators(self, sr: str) -> Sequence[ModeratorListItem]:
        root = await self._client.request('GET', f'/r/{sr}/about/moderators')
        return [load_moderator_list_item(d) for d in root['data']['children']]


    async def get_approved_user(self, sr: str, user: str) -> Optional[UserRelationshipItem]:
        root = await self._client.request('GET', f'/r/{sr}/about/contributors', params={'user': user})
        children = root['data']['children']
        return load_user_relationship_item(children[0]) if children else None

    async def get_wiki_contributor(self, sr: str, user: str) -> Optional[UserRelationshipItem]:
        root = await self._client.request('GET', f'/r/{sr}/about/wikicontributors', params={'user': user})
        children = root['data']['children']
        return load_user_relationship_item(children[0]) if children else None

    async def get_banned_user(self, sr: str, user: str) -> Optional[BannedUserRelationshipItem]:
        root = await self._client.request('GET', f'/r/{sr}/about/banned', params={'user': user})
        children = root['data']['children']
        return load_banned_user_relation_item(children[0]) if children else None

    async def get_muted_user(self, sr: str, user: str) -> Optional[UserRelationshipItem]:
        root = await self._client.request('GET', f'/r/{sr}/about/muted', params={'user': user})
        children = root['data']['children']
        return load_user_relationship_item(children[0]) if children else None

    async def get_wiki_banned_user(self, sr: str, user: str) -> Optional[BannedUserRelationshipItem]:
        root = await self._client.request('GET', f'/r/{sr}/about/wikibanned', params={'user': user})
        children = root['data']['children']
        return load_banned_user_relation_item(children[0]) if children else None
