
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_user_item import (
        ModeratorUserItem,
        ContributorUserItem,
        BannedUserItem,
        MutedUserItem,
    )

from ...models.load.subreddit_user_item import (
    load_moderator_user_item,
    load_contributor_user_item,
    load_banned_user_item,
    load_muted_user_item,
)
from .pull_users_SYNC import PullUsers
from .legacy_SYNC import Legacy
from .pull_SYNC import Pull

class Moderation:
    def __init__(self, client: Client):
        self._client = client
        self.legacy = Legacy(client)
        self.pull_users = PullUsers(client)
        self.pull = Pull(client)

    def get_moderator(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/moderators', params={'username': user})
        sequence = root['moderatorIds']
        object_mapping = root['moderators']
        return load_moderator_user_item(object_mapping[sequence[0]]) if sequence else None

    def get_moderator_invitation(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/moderators_invited', params={'username': user})
        sequence = root['moderatorIds']
        object_mapping = root['moderators']
        return load_moderator_user_item(object_mapping[sequence[0]]) if sequence else None

    def get_editable_moderator(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/moderators_editable', params={'username': user})
        sequence = root['moderatorIds']
        object_mapping = root['moderators']
        return load_moderator_user_item(object_mapping[sequence[0]]) if sequence else None

    def get_approved_contributor(self, sr: str, user: str) -> Optional[ContributorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/contributors', params={'username': user})
        sequence = root['approvedSubmitterIds']
        object_mapping = root['approvedSubmitters']
        return load_contributor_user_item(object_mapping[sequence[0]]) if sequence else None

    def get_banned_user(self, sr: str, user: str) -> Optional[BannedUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/banned', params={'username': user})
        sequence = root['bannedUserIds']
        object_mapping = root['bannedUsers']
        return load_banned_user_item(object_mapping[sequence[0]]) if sequence else None

    def get_muted_user(self, sr: str, user: str) -> Optional[MutedUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/muted', params={'username': user})
        sequence = root['mutedUserIds']
        object_mapping = root['mutedUsers']
        return load_muted_user_item(object_mapping[sequence[0]]) if sequence else None

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

    def add_approved_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'contributor',
            'name': user,
        }
        self._client.request('POST', '/api/friend', data=data)

    def leave_approved_contributor(self, sr: str, user: str) -> None:
        ...

    def remove_approved_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'contributor',
            'name': user,
        }
        self._client.request('POST', '/api/unfriend', data=data)

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
