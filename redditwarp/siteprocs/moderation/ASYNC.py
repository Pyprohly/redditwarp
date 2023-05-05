
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Union
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_user import (
        Moderator,
        ApprovedUser,
        BannedUser,
        MutedUser,
    )
    from ...models.moderation_action_log_entry import ModerationActionLogEntry

from functools import cached_property

from ...model_loaders.subreddit_user import (
    load_moderator,
    load_approved_user,
    load_banned_user,
    load_muted_user,
)
from .pull_users_ASYNC import PullUsers
from .legacy_ASYNC import Legacy
from .pull_ASYNC import Pull
from .note_ASYNC import Note
from ...util.base_conversion import to_base36
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.moderation.async1 import ModerationActionLogAsyncPaginator

class ModerationProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.legacy: Legacy = Legacy(client)
        ("""
            Legacy procedures for retrieving subreddit users.
            """)
        self.pull_users: PullUsers = PullUsers(client)
        ("""
            Procedures for retrieving subreddit users.
            """)
        self.pull: Pull = Pull(client)
        ("""
            Procedures for pulling moderation items.
            """)
        self.note: Note = Note(client)
        ("""
            Procedures for managing mod notes.
            """)

    def pull_actions(self, sr: str, amount: Optional[int] = None, *,
            action: str = '', mod: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModerationActionLogAsyncPaginator, ModerationActionLogEntry]:
        """Retrieve recent moderation actions from the mod log.

        .. hint::

           Moderator actions taken within a subreddit are logged to a mod log.
           Entries in the mod log last for 3 months before they become inaccessible.

        .. .PARAMETERS

        :param `str` sr:
            The target subreddit.
        :param `Optional[int]` amount:
            The number of items to retrieve.
        :param `str` action:
            Limit log entries to only those of a specified action.
        :param `str` mod:
            A comma-delimited list of moderator names to restrict the results to,
            or use the string `a` to restrict the results to actions performed by administrators.

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`\\[:class:`~.pagination.paginators.moderation.async1.ModerationActionLogAsyncPaginator`, :class:`~.models.moderation_action_log_entry.ModerationActionLogEntry`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                You do not have permission to view the mod log of the specified subreddit.
        """
        p = ModerationActionLogAsyncPaginator(self._client, f'/r/{sr}/about/log', action=action, mod=mod)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)


    async def get_moderator(self, sr: str, user: str) -> Optional[Moderator]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = await self._client.request('GET', f'/api/v1/{sr}/moderators', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator(object_map[order[0]]) if order else None

    async def get_moderator_invitation(self, sr: str, user: str) -> Optional[Moderator]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = await self._client.request('GET', f'/api/v1/{sr}/moderators_invited', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator(object_map[order[0]]) if order else None

    async def get_editable_moderator(self, sr: str, user: str) -> Optional[Moderator]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = await self._client.request('GET', f'/api/v1/{sr}/moderators_editable', params={'username': user})
        order = root['moderatorIds']
        object_map = root['moderators']
        return load_moderator(object_map[order[0]]) if order else None

    async def get_approved_user(self, sr: str, user: str) -> Optional[ApprovedUser]:
        """Get an approved user of a subreddit.

        .. .PARAMETERS

        :param `str` sr:
            Name of a subreddit.
        :param `str` user:
            Name of a user.

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.subreddit_user.ApprovedUser`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `SUBREDDIT_NOEXIST`:
                The target subreddit does not exist.
            + `SUBREDDIT_NO_ACCESS`:
                The subreddit cannot be accessed.
        """
        root = await self._client.request('GET', f'/api/v1/{sr}/contributors', params={'username': user})
        order = root['approvedSubmitterIds']
        object_map = root['approvedSubmitters']
        return load_approved_user(object_map[order[0]]) if order else None

    async def get_banned_user(self, sr: str, user: str) -> Optional[BannedUser]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = await self._client.request('GET', f'/api/v1/{sr}/banned', params={'username': user})
        order = root['bannedUserIds']
        object_map = root['bannedUsers']
        return load_banned_user(object_map[order[0]]) if order else None

    async def get_muted_user(self, sr: str, user: str) -> Optional[MutedUser]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = await self._client.request('GET', f'/api/v1/{sr}/muted', params={'username': user})
        order = root['mutedUserIds']
        object_map = root['mutedUsers']
        return load_muted_user(object_map[order[0]]) if order else None


    async def send_moderator_invite(self, sr: str, user: str, permissions: Sequence[str]) -> None:
        """Send a moderator invite.

        If the user is already invited, nothing happens. The permissions won't change.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `Sequence[str]` permissions:
            Values: `all`, `access`, `chat_config`, `chat_operator`, `config`,
            `flair`, `mail`, `posts`, `wiki`.

            Pass an empty sequence for no permissions.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty, or contains invalid characters.
            + `USER_DOESNT_EXIST`:
                The user specified by `user` does not exist.
            + `INVALID_PERMISSIONS`:
                An invalid permission was provided.
            + `ALREADY_MODERATOR`:
                The user is already a moderator.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - You don't have permission.
               - The target subreddit specified was empty.

            + `404`:
                The specified subreddit does not exist.
        """
        data = {
            'type': 'moderator_invite',
            'r': sr,
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def accept_moderator_invite(self, sr: str) -> None:
        """Accept a moderator invite.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_INVITE_FOUND`:
                You don't have a pendning invitation for the specified subreddit.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The subreddit specified was empty.
        """
        await self._client.request('POST', '/api/accept_moderator_invite', data={'r': sr})

    async def revoke_moderator_invite(self, sr: str, user: str) -> None:
        """Revoke a moderator invite.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                The `user` parameter was empty or the user doesn't exist.
            + `403`:
               - You don't have permission.
               - The target subreddit specified was empty.
        """
        data = {
            'type': 'moderator_invite',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def remove_moderator(self, sr: str, user: str) -> None:
        """Remove a moderator.

        Nothing happens if the specified user is not a moderator of the subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                The `user` parameter was empty or the user doesn't exist.
            + `403`:
               - You don't have permission.
               - The target subreddit specified was empty.
        """
        data = {
            'type': 'moderator',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def leave_moderator(self, sr_id: Union[int, str]) -> None:
        """Abdicate moderator status in a subreddit.

        .. warning::

            This action cannot be undone.

        Be careful with this endpoint. It's possible for a subreddit to not have any moderators.

        Nothing happens if the specified subreddit ID is not valid or the
        current user is not a moderator of the subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` sr_id:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        id36 = x if isinstance((x := sr_id), str) else to_base36(x)
        await self._client.request('POST', '/api/leavemoderator', data={'id': 't5_' + id36})

    async def set_moderator_permissions(self, sr: str, user: str, permissions: Sequence[str]) -> None:
        """Set the permissions of a moderator.

        Be careful with this endpoint. It's possible for a subreddit to not have any moderators.

        Nothing happens if the current user is not a moderator of the subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `Sequence[str]` permissions:
            Values: `all`, `access`, `chat_config`, `chat_operator`, `config`,
            `flair`, `mail`, `posts`, `wiki`.

            Pass an empty sequence for no permissions.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty, or contains invalid characters.
            + `USER_DOESNT_EXIST`:
                The user specified by `user` does not exist.
            + `INVALID_PERMISSION_TYPE`:
                The user specified by `user` isn't a moderator of the subreddit.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You don't have permission.
            + `404`:
                The specified subreddit does not exist.
        """
        data = {
            'type': 'moderator',
            'r': sr,
            'name': user,
            'permissions': ','.join('+' + p for p in permissions) if permissions else '-access',
        }
        await self._client.request('POST', '/api/setpermissions', data=data)

    async def set_moderator_invite_permissions(self, sr: str, user: str, permissions: Sequence[str]) -> None:
        """Set the permissions on a moderator invite.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `Sequence[str]` permissions:
            Values: `all`, `access`, `chat_config`, `chat_operator`, `config`,
            `flair`, `mail`, `posts`, `wiki`.

            Pass an empty sequence for no permissions.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty, or contains invalid characters.
            + `USER_DOESNT_EXIST`:
                The user specified by `user` does not exist.
            + `INVALID_PERMISSION_TYPE`:
                The user specified by `user` doesn't have a moderator invite to the subreddit.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You don't have permission.
            + `404`:
                The specified subreddit does not exist.
        """
        data = {
            'type': 'moderator_invite',
            'r': sr,
            'name': user,
            'permissions': ','.join('+' + p for p in permissions) if permissions else '-access',
        }
        await self._client.request('POST', '/api/setpermissions', data=data)

    async def add_approved_user(self, sr: str, user: str) -> None:
        """Add an approved user to a subreddit.

        If the user is already an approved user, nothing happens.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty, or contains invalid characters.
            + `USER_DOESNT_EXIST`:
                The user specified by `user` does not exist.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - You don't have permission.
               - The target subreddit specified was empty.

            + `404`:
                The specified subreddit does not exist.
        """
        data = {
            'type': 'contributor',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def remove_approved_user(self, sr: str, user: str) -> None:
        """Remove an approved user of a subreddit.

        If the user is already not an approved user, nothing happens.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty, or contains invalid characters.
            + `USER_DOESNT_EXIST`:
                The user specified by `user` does not exist.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                The `user` parameter was empty or the user doesn't exist.
            + `403`:
               - You don't have permission.
               - The target subreddit specified was empty.

            + `404`:
                The specified subreddit does not exist.
        """
        data = {
            'type': 'contributor',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def leave_approved_user(self, sr_id: Union[int, str]) -> None:
        """Abdicate approved user status in a subreddit.

        Nothing happens if the specified subreddit ID is not valid or the
        current user is not an approved user of the subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` sr_id:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        id36 = x if isinstance((x := sr_id), str) else to_base36(x)
        await self._client.request('POST', '/api/leavecontributor', data={'id': 't5_' + id36})

    async def ban_user(self, sr: str, user: str, *,
            duration: Optional[int] = None,
            reason: str = '',
            note: str = '',
            message: str = '') -> None:
        """Ban a user from a subreddit.

        Banning an already banned user does nothing. However, when banning an already
        banned user (as to change the ban reason or note), if the duration is changed
        then a new direct message will be issued to the user informing them of the
        duration change.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `Optional[int]` duration:
            Number of days they should be banned for, in the range of 1 to 999.

            To change the duration of a ban, re-issue this procedure with a new duration.
            A direct message is sent to the user informing them of the ban duration change.
        :param `str` reason:
            Ban reason. No longer than 100 characters.
        :param `str` note:
            A moderator note. No longer than 300 characters.
        :param `str` message:
            The message to include in the DM that is sent to the user.

            Specify markdown text.

            Note that a direct message is always sent to the banned user when a ban is issued.
            The ban message shows in the DM under a section called "Note from the moderators:".

            If empty string, no message or section "Note from the moderators:" is shown.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty, or contains invalid characters.
            + `USER_DOESNT_EXIST`:
                The user specified by `user` does not exist.
            + `BAD_NUMBER`:
                When `type: banned` or `type: wikibanned`,
                the number specified by `duration` is not within the range 1 to 999.
            + `TOO_LONG`:
               - The value specified by `reason` is over 100 characters.
               - The value specified by `note` is over 300 characters.

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - You don't have permission.
               - The target subreddit specified was empty.

            + `404`:
                The specified subreddit does not exist.
        """
        data = {
            'type': 'banned',
            'r': sr,
            'name': user,
            'ban_reason': reason,
            'ban_message': message,
            'note': note,
        }
        if duration is not None:
            data['duration'] = str(duration)

        await self._client.request('POST', '/api/friend', data=data)

    async def unban_user(self, sr: str, user: str) -> None:
        """Unban a user from a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises): Same as :meth:`~.remove_approved_user`.
        """
        data = {
            'type': 'banned',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def mute_user(self, sr: str, user: str, *, note: str = '') -> None:
        """Mute a user in a subreddit.

        Muting an already muted user does nothing.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `str` note:
            A moderator note. No longer than 300 characters.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            In addition to :meth:`~.add_approved_user`:

            + `TOO_LONG`:
                The value specified by `note` is over 300 characters.
        :raises redditwarp.http.exceptions.StatusCodeException:
            Same as :meth:`~.add_approved_user`.
        """
        data = {
            'type': 'muted',
            'r': sr,
            'name': user,
            'note': note,
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def unmute_user(self, sr: str, user: str) -> None:
        """Unmute a user in a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises): Same as :meth:`~.remove_approved_user`.
        """
        data = {
            'type': 'muted',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def add_wiki_contributor(self, sr: str, user: str) -> None:
        """Add a wiki contributor in a subreddit.

        Adding a user who is already a wiki contributor does nothing.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises): Same as :meth:`~.add_approved_user`.
        """
        data = {
            'type': 'wikicontributor',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/friend', data=data)

    async def remove_wiki_contributor(self, sr: str, user: str) -> None:
        """Remove a wiki contributor in a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises): Same as :meth:`~.remove_approved_user`.
        """
        data = {
            'type': 'wikicontributor',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)

    async def ban_wiki_contributor(self, sr: str, user: str, *,
            duration: Optional[int] = None,
            reason: str = '',
            note: str = '') -> None:
        """Ban a wiki contributor in a subreddit.

        Adding a user who is already a wiki contributor does nothing.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `Optional[int]` duration:
            Number of days they should be banned for, in the range of 1 to 999.
        :param `str` reason:
            Ban reason. No longer than 100 characters.
        :param `str` note:
            A moderator note. No longer than 300 characters.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            In addition to :meth:`~.add_approved_user`:

            + `TOO_LONG`:
               - The value specified by `reason` is over 100 characters.
               - The value specified by `note` is over 300 characters.

        :raises redditwarp.http.exceptions.StatusCodeException:
            Same as :meth:`~.add_approved_user`.
        """
        data = {
            'type': 'banned',
            'r': sr,
            'name': user,
            'ban_reason': reason,
            'note': note,
        }
        if duration is not None:
            data['duration'] = str(duration)

        await self._client.request('POST', '/api/friend', data=data)

    async def unban_wiki_contributor(self, sr: str, user: str) -> None:
        """Unban a wiki contributor in a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises): Same as :meth:`~.remove_approved_user`.
        """
        data = {
            'type': 'wikibanned',
            'r': sr,
            'name': user,
        }
        await self._client.request('POST', '/api/unfriend', data=data)


    class RemovalReason:
        def __init__(self, outer: ModerationProcedures) -> None:
            self._outer = outer
            self._client = outer._client

        async def create(self, sr: str, title: str, message: str) -> str:
            """Create a removal reason.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` title:
                A title for this removal reason.
            :param `str` message:
                The removal reason message.

            .. .RETURNS

            :returns: The newly created removal reason ID.
            :rtype: `str`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `MOD_REQUIRED`:
                   - There is no user context.
                   - The current user is not a moderator of the subreddit.

                + `NO_TEXT`:
                   - The `title` parameter was not specified or was empty.
                   - The `message` parameter was not specified or was empty.

                + `TOO_LONG`:
                   - The value specified for `title` is over 50 characters.
                   - The value specified for `message` is over 10000 characters.

            :raises redditwarp.http.exceptions.StatusCodeException:
                + `500`:
                    The target subreddit does not exist.
            """
            data = {'title': title, 'message': message}
            root = await self._client.request('POST', f'/api/v1/{sr}/removal_reasons', data=data)
            return root['id']

        async def retrieve(self, sr: str) -> Mapping[str, tuple[str, str]]:
            """Get a list of removal reasons.

            .. .PARAMETERS

            :param `str` sr:

            .. .RETURNS

            :returns: A mapping of removal reason IDs to tuples of `(title, message)`.
            :rtype: `Mapping`\\[`str`, `tuple`\\[`str`, `str`]]

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `MOD_REQUIRED`:
                   - There is no user context.
                   - The current user is not a moderator of the subreddit.

                + `SUBREDDIT_NOEXIST`:
                    The target subreddit does not exist.
            """
            root = await self._client.request('GET', f'/api/v1/{sr}/removal_reasons')
            order = root['order']
            object_map = root['data']
            return {
                y: (m['title'], m['message'])
                for y in order for m in [object_map[y]]
            }

        async def replace(self, sr: str, idt: str, title: str, message: str) -> None:
            """Update a removal reason's title and message.

            Both parameters `title` and `message` must be specified otherwise
            a `NO_TEXT` API error is returned.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` idt:
                A removal reason ID.
            :param `str` title:
            :param `str` message:

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `MOD_REQUIRED`:
                   - There is no user context.
                   - The current user is not a moderator of the subreddit.

                + `SUBREDDIT_NOEXIST`:
                    The target subreddit does not exist.
                + `INVALID_ID`:
                    The specified removal reason ID was not found.
                + `NO_TEXT`:
                   - The `title` parameter was not specified or was empty.
                   - The `message` parameter was not specified or was empty.

                + `TOO_LONG`:
                   - The value specified for `title` is over 50 characters.
                   - The value specified for `message` is over 10000 characters.
            """
            data = {'title': title, 'message': message}
            await self._client.request('PUT', f'/api/v1/{sr}/removal_reasons/{idt}', data=data)

        async def delete(self, sr: str, idt: str) -> None:
            """Delete a removal reason.

            If the specified removal reason ID did not exist, nothing happens.

            .. .PARAMETERS

            :param `str` sr:
            :param `str` idt:

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `MOD_REQUIRED`:
                   - There is no user context.
                   - The current user is not a moderator of the subreddit.

                + `SUBREDDIT_NOEXIST`:
                    The target subreddit does not exist.
                + `INVALID_ID`:
                    The specified removal reason ID was not found.
            """
            await self._client.request('DELETE', f'/api/v1/{sr}/removal_reasons/{idt}')

    removal_reason: cached_property[RemovalReason] = cached_property(RemovalReason)
