
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional, Mapping, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_user_item import (
        ModeratorUserItem,
        ContributorUserItem,
        BannedUserItem,
        MutedUserItem,
    )
    from ...models.moderation_action_log_entry import ModerationActionLogEntry
    from ...models.moderation_note import ModerationNote, ModerationUserNote

from functools import cached_property

from ...models.load.subreddit_user_item import (
    load_moderator_user_item,
    load_contributor_user_item,
    load_banned_user_item,
    load_muted_user_item,
)
from ...models.load.moderation_note import load_moderation_user_note
from .pull_users_SYNC import PullUsers
from .legacy_SYNC import Legacy
from .pull_SYNC import Pull
from ...util.base_conversion import to_base36
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.implementations.moderation.sync import ModerationActionLogPaginator
from ...pagination.implementations.moderation.note_pulls_sync import ModerationNotePaginator
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ... import http

class ModerationProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.legacy: Legacy = Legacy(client)
        self.pull_users: PullUsers = PullUsers(client)
        self.pull: Pull = Pull(client)

    def pull_actions(self, sr: str, amount: Optional[int] = None, *,
            action: str = '', mod: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModerationActionLogPaginator, ModerationActionLogEntry]:
        p = ModerationActionLogPaginator(self._client, f'/r/{sr}/about/log', action=action, mod=mod)
        return ImpartedPaginatorChainingIterator(p, amount)

    def get_moderator(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/moderators', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator_user_item(object_map[order[0]]) if order else None

    def get_moderator_invitation(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/moderators_invited', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator_user_item(object_map[order[0]]) if order else None

    def get_editable_moderator(self, sr: str, user: str) -> Optional[ModeratorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/moderators_editable', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator_user_item(object_map[order[0]]) if order else None

    def get_approved_contributor(self, sr: str, user: str) -> Optional[ContributorUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/contributors', params={'username': user})
        order = root['approvedSubmitterIds']
        object_map = root['approvedSubmitters']
        return load_contributor_user_item(object_map[order[0]]) if order else None

    def get_banned_user(self, sr: str, user: str) -> Optional[BannedUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/banned', params={'username': user})
        order = root['bannedUserIds']
        object_map = root['bannedUsers']
        return load_banned_user_item(object_map[order[0]]) if order else None

    def get_muted_user(self, sr: str, user: str) -> Optional[MutedUserItem]:
        root = self._client.request('GET', f'/api/v1/{sr}/muted', params={'username': user})
        order = root['mutedUserIds']
        object_map = root['mutedUsers']
        return load_muted_user_item(object_map[order[0]]) if order else None

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

    def leave_moderator(self, subreddit_id: int) -> None:
        self._client.request('POST', '/api/leavemoderator', data={'id': 't5_' + to_base36(subreddit_id)})

    def remove_moderator(self, sr: str, user: str) -> None:
        data = {
            'r': sr,
            'type': 'moderator',
            'name': user,
        }
        self._client.request('POST', '/api/unfriend', data=data)

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

    def leave_approved_contributor(self, subreddit_id: int) -> None:
        self._client.request('POST', '/api/leavecontributor', data={'id': 't5_' + to_base36(subreddit_id)})

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

    class _removal_reason:
        def __init__(self, outer: ModerationProcedures) -> None:
            self._outer = outer
            self._client = outer._client

        def create(self, sr: str, title: str, message: str) -> int:
            data = {'title': title, 'message': message}
            root = self._client.request('POST', f'/api/v1/{sr}/removal_reasons', data=data)
            return int(root['id'], 36)

        def retrieve_map(self, sr: str) -> Mapping[str, tuple[str, str]]:
            root = self._client.request('GET', f'/api/v1/{sr}/removal_reasons')
            order = root['order']
            object_map = root['data']
            return {
                y: (m['title'], m['message'])
                for y in order for m in [object_map[y]]
            }

        def update(self, sr: str, reason_id: str, title: str, message: str) -> None:
            data = {'title': title, 'message': message}
            self._client.request('PUT', f'/api/v1/{sr}/removal_reasons/{reason_id}', data=data)

        def delete(self, sr: str, reason_id: str) -> None:
            self._client.request('DELETE', f'/api/v1/{sr}/removal_reasons/{reason_id}')

    removal_reason: cached_property[_removal_reason] = cached_property(_removal_reason)

    class _note:
        def __init__(self, outer: ModerationProcedures) -> None:
            self._outer = outer
            self._client = outer._client

        def create_user_note(self, subreddit: str, user: str, note: str, *,
                label: str = '',
                anchor_submission_id: Optional[int] = None,
                anchor_comment_id: Optional[int] = None) -> ModerationNote:
            mep = (anchor_submission_id, anchor_comment_id)
            if len(mep) - mep.count(None) > 1:
                raise TypeError('mutually exclusive parameters: `anchor_submission_id`, `anchor_comment_id)`.')

            reddit_id = ''
            if anchor_submission_id is not None:
                reddit_id = 't3_' + to_base36(anchor_submission_id)
            elif anchor_comment_id is not None:
                reddit_id = 't1_' + to_base36(anchor_comment_id)

            params = {'subreddit': subreddit, 'user': user, 'note': note, 'label': label, 'reddit_id': reddit_id}
            root = self._client.request('POST', '/api/mod/notes', params=params)
            return load_moderation_user_note(root['created'])

        def pulls(self,
            subreddit: str,
            user: str,
            amount: Optional[int] = None,
            *,
            type: Optional[str] = None,
        ) -> ImpartedPaginatorChainingIterator[ModerationNotePaginator, ModerationUserNote]:
            p = ModerationNotePaginator(
                client=self._client,
                uri='/api/mod/notes',
                subreddit=subreddit,
                user=user,
                type=type,
            )
            return ImpartedPaginatorChainingIterator(p, amount)

        def delete(self, note_uuid: str, subreddit: str, user: str) -> None:
            params = {'note_id': 'ModNote_' + note_uuid, 'subreddit': subreddit, 'user': user}
            self._client.request('DELETE', '/api/mod/notes', params=params)

        def get_latest_user_note(self, subreddit: str, user: str) -> Optional[ModerationUserNote]:
            params = {'subreddits': subreddit, 'users': user}
            try:
                root = self._client.request('GET', '/api/mod/notes/recent', params=params)
            except http.exceptions.StatusCodeException as e:
                if e.status_code == 400:
                    return None
                raise
            return load_moderation_user_note(root['mod_notes'][0])

        def bulk_get_latest_user_note(self, pairs: Iterable[tuple[str, str]]) -> CallChunkChainingIterator[Optional[ModerationUserNote]]:
            def mass_get_latest_user_note(pairs: Sequence[tuple[str, str]]) -> Sequence[Optional[ModerationUserNote]]:
                subreddits, users = tuple(zip(*pairs))
                subreddits_str = ','.join(subreddits)
                users_str = ','.join(users)
                params = {'subreddits': subreddits_str, 'users': users_str}
                try:
                    root = self._client.request('GET', '/api/mod/notes/recent', params=params)
                except http.exceptions.StatusCodeException as e:
                    if e.status_code == 400:
                        return [None]
                    raise
                return [
                    (None if note_obj is None else load_moderation_user_note(note_obj))
                    for note_obj in root['mod_notes']
                ]

            return CallChunkChainingIterator(CallChunk(mass_get_latest_user_note, chunk) for chunk in chunked(pairs, 500))

    note: cached_property[_note] = cached_property(_note)
