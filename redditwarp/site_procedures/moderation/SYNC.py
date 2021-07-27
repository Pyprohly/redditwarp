
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.moderator_list_item import ModeratorListItem
    from ...models.user_relationship_item import UserRelationshipItem, BannedUserRelationshipItem

from ...models.load.moderator_list_item import load_moderator_list_item
from ...models.load.user_relationship_item import load_user_relationship_item, load_banned_user_relation_item
from .pull_users_SYNC import PullUsers
from .legacy_SYNC import Legacy

class Moderation:
    def __init__(self, client: Client):
        self._client = client
        self.legacy = Legacy(client)
        self.pull_users = PullUsers(client)

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

    def send_moderator_invite(self, sr: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'r': sr,
            'type': 'moderator_invite',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        self._client.request('POST', '/api/friend', data=data)

    def accept_moderator_invite(self, sr: str, user: str) -> None:
        self._client.request('POST', '/api/accept_moderator_invite', data={'r': sr})

    def revoke_moderator_invite(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'moderator_invite',
            'name': user,
        }
        self._client.request('POST', '/api/friend', data=data)

    def set_moderator_permissions(self, sr: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'r': sr,
            'type': 'moderator',
            'name': user,
            'permissions': ','.join('+' + i for i in permissions),
        }
        self._client.request('POST', '/api/setpermissions', data=data)

    def set_moderator_invite_permissions(self, sr: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'r': sr,
            'type': 'moderator_invite',
            'name': user,
            'permissions': ','.join('+' + i for i in permissions),
        }
        self._client.request('POST', '/api/setpermissions', data=data)

    def ban_user(self, sr: str, user: str, *,
            reason: str = '',
            note: str = '',
            duration: Optional[int] = None,
            message: str = '') -> None:
        data = {
            'r': sr,
            'type': 'banned',
            'name': user,
            'ban_reason': reason,
            'note': note,
            'ban_message': message,
        }
        if duration is not None:
            data['duration'] = str(duration)

        self._client.request('POST', '/api/friend', data=data)

    def unban_user(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'banned',
            'name': user,
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def mute_user(self, sr: str, user: str, *, note: str = '') -> None:
        data = {
            'r': sr,
            'type': 'muted',
            'name': user,
            'note': note,
        }
        self._client.request('POST', '/api/friend', data=data)

    def unmute_user(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'muted',
            'name': user,
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def add_approved_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'contributor',
            'name': user,
        }
        self._client.request('POST', '/api/friend', data=data)

    def remove_approved_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'contributor',
            'name': user,
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def ban_wiki_contributor(self, sr: str, user: str, *,
            reason: str = '',
            note: str = '',
            duration: Optional[int] = None) -> None:
        data = {
            'r': sr,
            'type': 'banned',
            'name': user,
            'ban_reason': reason,
            'note': note,
        }
        if duration is not None:
            data['duration'] = str(duration)

        self._client.request('POST', '/api/friend', data=data)

    def unban_wiki_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'wikibanned',
            'name': user,
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def add_approved_wiki_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'wikicontributor',
            'name': user,
        }
        self._client.request('POST', '/api/friend', data=data)

    def remove_approved_wiki_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'wikicontributor',
            'name': user,
        }
        self._client.request('POST', '/api/unfriend', data=data)
