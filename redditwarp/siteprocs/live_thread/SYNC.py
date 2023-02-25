
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.live_thread_SYNC import LiveThread, LiveUpdate

from ...models.live_thread import ContributorList, Contributor
from ...model_loaders.live_thread_SYNC import load_live_thread, load_live_update
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...util.base_conversion import to_base36
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.live_thread_sync1 import LiveUpdateListingPaginator
from ... import http

class LiveThreadProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def get(self, idt: str) -> Optional[LiveThread]:
        """Get a live thread.

        .. .PARAMETERS

        :param `str` idt:

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.live_thread_SYNC.LiveThread`]
        """
        try:
            root = self._client.request('GET', f'/live/{idt}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return load_live_thread(root['data'], self._client)

    def bulk_fetch(self, idts: Iterable[str]) -> CallChunkChainingIterator[LiveThread]:
        """Bulk fetch live threads.

        Entries are returned in the same order as specified.

        If one of the IDs in a batch does not exist then a 500 HTTP error is returned.

        .. .PARAMETERS

        :param `Iterable[str]` idts:

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[:class:`~.models.live_thread_SYNC.LiveThread`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `500`:
                A specified ID does not exist.
        """
        def mass_fetch(idts: Sequence[str]) -> Sequence[LiveThread]:
            idts_str = ','.join(idts)
            root = self._client.request('GET', '/api/live/by_id/' + idts_str)
            return [load_live_thread(o['data'], self._client) for o in root['data']['children']]

        return CallChunkChainingIterator(CallChunk(mass_fetch, idfs) for idfs in chunked(idts, 100))

    def create(self,
        title: str,
        description: str = '',
        resources: str = '',
        nsfw: bool = False,
    ) -> str:
        """Create a live thread.

        .. .PARAMETERS

        :param `str` title:
            Title. A string no longer than 120 characters.
        :param `str` description:
            Description. Markdown text. This text is displayed under the title.

            Default: empty string.
        :param `str` resources:
            The resources. Markdown text. This text is displayed on the sidebar.

            Default: empty string.
        :param `bool` nsfw:
            Whether to mark the live thread as NSFW.

            Default false.

        .. .RETURNS

        :returns: The ID of the newly created live thread.
        :rtype: `str`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
                The specified title was empty.
            + `RATELIMIT`:
                You must wait one minute before creating another live thread.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('title', title)
            yield ('description', description)
            yield ('resources', resources)
            if nsfw: yield ('nsfw', '1')

        root = self._client.request('POST', '/api/live/create', data=dict(g()))
        return root['json']['data']['id']

    def config(self,
        idt: str,
        title: str,
        description: str = '',
        resources: str = '',
        nsfw: bool = False,
    ) -> None:
        """Configure the live thread.

        Requires the `settings` live thread permission.

        All parameters must be specified otherwise they will be set to their effective defaults.

        .. .PARAMETERS

        :(parameters): Same as :meth:`.create`.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have the `settings` live thread permission.
               - You do not have permission.

            + `404`:
                The specified live thread does not exist.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('title', title)
            yield ('description', description)
            yield ('resources', resources)
            if nsfw: yield ('nsfw', '1')

        self._client.request('POST', f'/api/live/{idt}/edit', data=dict(g()))

    def close(self, idt: str) -> None:
        """Close a live thread.

        This permanently closes the live thread, disallowing future updates.

        .. .PARAMETERS

        :param `str` idt:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES


        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have the `close` permission.
               - The live thread is already closed.

            + `404`:
                The specified live thread does not exist.
        """
        self._client.request('POST', f'/api/live/{idt}/close_thread')

    def get_update(self, idt: str, uuid: str) -> LiveUpdate:
        """Get a specific live update in a live thread.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified live thread ID or live update ID does not exist.
        """
        root = self._client.request('GET', f'/live/{idt}/updates/{uuid}')
        return load_live_update(root['data'], self._client)

    def pull(self, idt: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[LiveUpdateListingPaginator, LiveUpdate]:
        """Pull live updates from a live thread.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` uuid:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.live_thread_sync1.LiveUpdateListingPaginator`, :class:`~.models.live_thread_SYNC.LiveUpdate`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified live thread does not exist.
        """
        p = LiveUpdateListingPaginator(self._client, f'/live/{idt}')
        return ImpartedPaginatorChainingIterator(p, amount)

    def create_update(self, idt: str, body: str) -> None:
        """Post a live update to the thread.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` body:
            Markdown text.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
                The `body` parameter was empty.
        """
        self._client.request('POST', f'/api/live/{idt}/update', data={'body': body})

    def strike_update(self, idt: str, uuid: str) -> None:
        """Strike the content of a live update.

        Requires that specified update must have been authored by the user
        or that you have the `edit` permission.

        Striken updates cannot be unstriken.

        If an already striken item is striken it is treated as a success.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_THING_ID`:
               - The live update specified by `uuid` was empty.
               - The live update specified by `uuid` does not exist.

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You don't have permission.
            + `404`:
                The live thread specified by `idt` does not exist.
        """
        self._client.request('POST', f'/api/live/{idt}/strike_update', data={'id': 'LiveUpdate_' + uuid})

    def delete_update(self, idt: str, uuid: str) -> None:
        """Delete a live update.

        Requires that specified update must have been authored by the current user
        or that you have the `edit` permission.

        If an already deleted update is specified, the action will be treated as a success.
        But specifying a non-existing update ID will cause a `NO_THING_ID` API error.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_THING_ID`:
               - The live update specified by `uuid` was empty.
               - The live update specified by `uuid` does not exist.

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You don't have permission.
            + `404`:
                The live thread specified by `idt` does not exist.
        """
        self._client.request('POST', f'/api/live/{idt}/delete_update', data={'id': 'LiveUpdate_' + uuid})

    def list_contributors(self, idt: str) -> ContributorList:
        """Get a list of users that contribute to a thread.

        Returns an object with a `.contributors` attribute containing
        a list of contributors, and a `.invitations` attribute containing
        a list of users that have been invited to be contributors.

        The `.invitations` list will be empty if the current user does not have
        the `manage` live thread permission.

        .. .PARAMETERS

        :param `str` idt:

        .. .RETURNS

        :rtype: :class:`~.models.live_thread.ContributorList`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The live thread specified by `idt` does not exist.
        """
        root = self._client.request('GET', f'/live/{idt}/contributors')
        if isinstance(root, (dict, Mapping)):
            return ContributorList([Contributor(d) for d in root['data']['children']], ())

        contributors = [Contributor(d) for d in root[0]['data']['children']]
        invitations = [Contributor(d) for d in root[0]['data']['children']]
        return ContributorList(contributors, invitations)

    def send_contributor_invite(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        """Invite a user to contribute to the live thread.

        Requires the `manage` live thread permission.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` user:
        :param `Iterable[str]` permissions:
            Values: empty string, `all`, `close`, `discussions`, `edit`, `manage`,
            `settings`, `update`.

            Default: empty string. On the interface it'll say 'no permissions'.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `NO_USER`:
                The `user` parameter was empty.
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
            + `LIVEUPDATE_ALREADY_CONTRIBUTOR`:
                The specified user is already a contributor or has already been invited.
            + `INVALID_PERMISSIONS`:
                An invalid permission was specified.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - You do not have the `manage` permission.

            + `404`:
                The specified live thread does not exist.
        """
        data = {
            'type': 'liveupdate_contributor_invite',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        self._client.request('POST', f'/api/live/{idt}/invite_contributor', data=data)

    def accept_contributor_invite(self, idt: str) -> None:
        """Accept an invitation to contribute to a live thread.

        .. .PARAMETERS

        :param `str` idt:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `LIVEUPDATE_NO_INVITE_FOUND`:
                You don't have an invitation for the specified live thread.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified live thread does not exist.
        """
        self._client.request('POST', f'/api/live/{idt}/accept_contributor_invite')

    def revoke_contributor_invite(self, idt: str, user_id: int) -> None:
        """Revoke an outstanding contributor invite.

        Requires the `manage` live thread permission.

        If attempting to remove the invite for a user that was not invited,
        the action is treated as a success.

        .. .PARAMETERS

        :param `str` idt:
        :param `int` user_id:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
               - There is no user context.
               - You do not have the `manage` permission.
               - You do not have permission.
        """
        id36 = to_base36(user_id)
        self._client.request('POST', f'/api/live/{idt}/rm_contributor_invite', data={'id': 't2_' + id36})

    def leave_contributor(self, idt: str) -> None:
        """Abdicate contributorship of the thread.

        It is possible to leave a live thread and not have any contributors to it.

        If leaving a live thread you were not a contributor to,
        the action is treated as a success.

        .. .PARAMETERS

        :param `str` idt:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified live thread does not exist.
        """
        self._client.request('POST', f'/api/live/{idt}/leave_contributor')

    def remove_contributor(self, idt: str, user_id: int) -> None:
        """Revoke another user's contributorship.

        Requires the `manage` live thread permission.

        It is possible to remove your own contributorship, having the same effect as
        :meth:`.leave_contributor`.

        If attempting to remove the invite for a user that was not invited,
        the action is treated as a success.

        .. .PARAMETERS

        :param `str` idt:
        :param `int` user_id:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
              - There is no user context.
              - You are not a contributor to the live thread that has the `manage` permission.

            + `404`:
                The specified live thread does not exist.
            + `500`:
                The specified user was invalid.
        """
        id36 = to_base36(user_id)
        self._client.request('POST', f'/api/live/{idt}/rm_contributor', data={'id': 't2_' + id36})

    def set_contributor_permissions(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        """Change a contributor's permissions.

        Requires the `manage` live thread permission.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` user:
        :param `Iterable[str]` permissions:
            Same as :meth:`.send_contributor_invite`.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty.
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
            + `INVALID_PERMISSIONS`:
                An invalid permission was specified.
            + `LIVEUPDATE_NOT_CONTRIBUTOR`:
                The specified user is not a contributor.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
              - There is no user context.
              - You do not have the `manage` live thread permission.

            + `404`:
                The specified live thread does not exist.
        """
        data = {
            'type': 'liveupdate_contributor',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        self._client.request('POST', f'/api/live/{idt}/set_contributor_permissions', data=data)

    def set_contributor_invite_permissions(self, idt: str, user: str, permissions: Iterable[str]) -> None:
        """Change a contributor invite's permissions.

        .. .PARAMETERS

        :param `str` idt:
        :param `str` user:
        :param `Iterable[str]` permissions:
            Same as :meth:`.send_contributor_invite`.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The `user` parameter was empty.
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
            + `INVALID_PERMISSIONS`:
                An invalid permission was specified.
            + `LIVEUPDATE_NO_INVITE_FOUND`:
                The specified user does not have an invite.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
              - There is no user context.
              - You do not have the `manage` live thread permission.

            + `404`:
                The specified live thread does not exist.
        """
        data = {
            'type': 'liveupdate_contributor_invite',
            'name': user,
            'permissions': ','.join('+' + p for p in permissions),
        }
        self._client.request('POST', f'/api/live/{idt}/set_contributor_permissions', data=data)
