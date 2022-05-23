
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_user_item import (
        ModeratorUserItem,
        ContributorUserItem,
        BannedUserItem,
        MutedUserItem,
    )
    from ...models.moderation_action_log_entry import ModerationActionLogEntry

from functools import cached_property

from ...model_loaders.subreddit_user_item import (
    load_moderator_user_item,
    load_contributor_user_item,
    load_banned_user_item,
    load_muted_user_item,
)
from .pull_users_ASYNC import PullUsers
from .legacy_ASYNC import Legacy
from .pull_ASYNC import Pull
from .note_ASYNC import Note
from ...util.base_conversion import to_base36
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.moderation.async1 import ModerationActionLogAsyncPaginator

class ModerationProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.legacy: Legacy = Legacy(client)
        self.pull_users: PullUsers = PullUsers(client)
        self.pull: Pull = Pull(client)
        self.note: Note = Note(client)

    def pull_actions(self, sr: str, amount: Optional[int] = None, *,
            action: str = '', mod: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModerationActionLogAsyncPaginator, ModerationActionLogEntry]:
        p = ModerationActionLogAsyncPaginator(self._client, f'/r/{sr}/about/log', action=action, mod=mod)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def get_moderator(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = await self._client.request('GET', f'/api/v1/{sr}/moderators', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator_user_item(object_map[order[0]]) if order else None

    async def get_moderator_invitation(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = await self._client.request('GET', f'/api/v1/{sr}/moderators_invited', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator_user_item(object_map[order[0]]) if order else None

    async def get_editable_moderator(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = await self._client.request('GET', f'/api/v1/{sr}/moderators_editable', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator_user_item(object_map[order[0]]) if order else None

    async def get_approved_contributor(self, sr: str, user: str) -> Optional[ContributorUserItem]:
        root = await self._client.request('GET', f'/api/v1/{sr}/contributors', params={'username': user})
        order = root['approvedSubmitterIds']
        object_map = root['approvedSubmitters']
        return load_contributor_user_item(object_map[order[0]]) if order else None

    async def get_banned_user(self, sr: str, user: str) -> Optional[BannedUserItem]:
        root = await self._client.request('GET', f'/api/v1/{sr}/banned', params={'username': user})
        order = root['bannedUserIds']
        object_map = root['bannedUsers']
        return load_banned_user_item(object_map[order[0]]) if order else None

    async def get_muted_user(self, sr: str, user: str) -> Optional[MutedUserItem]:
        root = await self._client.request('GET', f'/api/v1/{sr}/muted', params={'username': user})
        order = root['mutedUserIds']
        object_map = root['mutedUsers']
        return load_muted_user_item(object_map[order[0]]) if order else None

    async def send_moderator_invite(self, sr: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'r': sr,
            'type': 'moderator_invite',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def accept_moderator_invite(self, sr: str, user: str) -> None:
        await self._client.request('POST', '/api/accept_moderator_invite', data={'r': sr})

    async def revoke_moderator_invite(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'moderator_invite',
            'name': user,
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def leave_moderator(self, subreddit_id: int) -> None:
        await self._client.request('POST', '/api/leavemoderator', data={'id': 't5_' + to_base36(subreddit_id)})

    async def remove_moderator(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'moderator',
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def set_moderator_permissions(self, sr: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'r': sr,
            'type': 'moderator',
            'name': user,
            'permissions': ','.join('+' + i for i in permissions),
        }
        await self._client.request('POST', '/api/setpermissions', data=data)

    async def set_moderator_invite_permissions(self, sr: str, user: str, permissions: Iterable[str]) -> None:
        data = {
            'r': sr,
            'type': 'moderator_invite',
            'name': user,
            'permissions': ','.join('+' + i for i in permissions),
        }
        await self._client.request('POST', '/api/setpermissions', data=data)

    async def add_approved_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'contributor',
            'name': user,
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def leave_approved_contributor(self, subreddit_id: int) -> None:
        await self._client.request('POST', '/api/leavecontributor', data={'id': 't5_' + to_base36(subreddit_id)})

    async def remove_approved_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'contributor',
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def ban_user(self, sr: str, user: str, *,
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

        await self._client.request('POST', '/api/friend', data=data)

    async def unban_user(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'banned',
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def mute_user(self, sr: str, user: str, *, note: str = '') -> None:
        data = {
            'r': sr,
            'type': 'muted',
            'name': user,
            'note': note,
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def unmute_user(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'muted',
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def add_approved_wiki_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'wikicontributor',
            'name': user,
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def remove_approved_wiki_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'wikicontributor',
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def ban_wiki_contributor(self, sr: str, user: str, *,
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

        await self._client.request('POST', '/api/friend', data=data)

    async def unban_wiki_contributor(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'wikibanned',
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    class _removal_reason:
        def __init__(self, outer: ModerationProcedures) -> None:
            self._outer = outer
            self._client = outer._client

        async def create(self, sr: str, title: str, message: str) -> int:
            data = {'title': title, 'message': message}
            root = await self._client.request('POST', f'/api/v1/{sr}/removal_reasons', data=data)
            return int(root['id'], 36)

        async def retrieve_map(self, sr: str) -> Mapping[str, tuple[str, str]]:
            root = await self._client.request('GET', f'/api/v1/{sr}/removal_reasons')
            order = root['order']
            object_map = root['data']
            return {
                y: (m['title'], m['message'])
                for y in order for m in [object_map[y]]
            }

        async def update(self, sr: str, reason_id: str, title: str, message: str) -> None:
            data = {'title': title, 'message': message}
            await self._client.request('PUT', f'/api/v1/{sr}/removal_reasons/{reason_id}', data=data)

        async def delete(self, sr: str, reason_id: str) -> None:
            await self._client.request('DELETE', f'/api/v1/{sr}/removal_reasons/{reason_id}')

    removal_reason: cached_property[_removal_reason] = cached_property(_removal_reason)
