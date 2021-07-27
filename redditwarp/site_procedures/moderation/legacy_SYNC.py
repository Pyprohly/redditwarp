
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_relationship_item import (
        UserRelationshipItem,
        BannedUserRelationshipItem,
    )
    from ...models.moderator_list_item import ModeratorListItem

from ...models.load.moderator_list_item import load_moderator_list_item
from ...models.load.user_relationship_item import load_user_relationship_item, load_banned_user_relation_item

from .legacy_pull_users_SYNC import LegacyPullUsers

class Legacy:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull_users = LegacyPullUsers(client)

    def list_moderators(self, sr: str) -> Sequence[ModeratorListItem]:
        root = self._client.request('GET', f'/r/{sr}/about/moderators')
        return [load_moderator_list_item(d) for d in root['data']['children']]

    def get_banned_user_item(self, sr: str, user: str) -> Optional[BannedUserRelationshipItem]:
        root = self._client.request('GET', f'/r/{sr}/about/banned', params={'user': user})
        children = root['data']['children']
        return load_banned_user_relation_item(children[0]) if children else None

    def get_muted_user_item(self, sr: str, user: str) -> Optional[UserRelationshipItem]:
        root = self._client.request('GET', f'/r/{sr}/about/muted', params={'user': user})
        children = root['data']['children']
        return load_user_relationship_item(children[0]) if children else None

    def get_approved_contributor_item(self, sr: str, user: str) -> Optional[UserRelationshipItem]:
        root = self._client.request('GET', f'/r/{sr}/about/contributors', params={'user': user})
        children = root['data']['children']
        return load_user_relationship_item(children[0]) if children else None

    def get_wiki_banned_user_item(self, sr: str, user: str) -> Optional[BannedUserRelationshipItem]:
        root = self._client.request('GET', f'/r/{sr}/about/wikibanned', params={'user': user})
        children = root['data']['children']
        return load_banned_user_relation_item(children[0]) if children else None

    def get_approved_wiki_contributor_item(self, sr: str, user: str) -> Optional[UserRelationshipItem]:
        root = self._client.request('GET', f'/r/{sr}/about/wikicontributors', params={'user': user})
        children = root['data']['children']
        return load_user_relationship_item(children[0]) if children else None
