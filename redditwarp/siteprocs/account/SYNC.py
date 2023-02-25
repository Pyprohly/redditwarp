
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Mapping, Any
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.my_account_SYNC import MyAccount
    from ...models.user_relationship import UserRelationship, FriendRelationship
    from ...models.trophy import Trophy
    from ...models.karma_breakdown_entry import KarmaBreakdownEntry
    from ...types import JSON_ro

from .pull_subreddits_SYNC import PullSubreddits
from ...model_loaders.my_account_SYNC import load_account
from ...model_loaders.user_relationship import load_user_relationship, load_friend_relationship
from ...model_loaders.karma_breakdown_entry import load_karma_breakdown_entry
from ...model_loaders.trophy import load_trophy
from ...util.base_conversion import to_base36
from ... import exceptions
from ...http import exceptions as http_exceptions

class AccountProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull_subreddits: PullSubreddits = PullSubreddits(client)

    def fetch(self) -> MyAccount:
        """Fetch information about the currently logged in user.

        .. .RETURNS

        :rtype: :class:`~.models.my_account_SYNC.MyAccount`

        .. .RAISES

        :raises redditwarp.exceptions.OperationException:
            There is no user context.
        """
        root = self._client.request('GET', '/api/v1/me')
        if len(root) < 6:
            raise exceptions.RejectedResultException('no user context')
        return load_account(root, self._client)

    def get_preferences(self) -> Mapping[str, Any]:
        """Retrieve the current user's preferences.

        .. .RETURNS

        :rtype: `Mapping`\\[`str`, `Any`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        return self._client.request('GET', '/api/v1/me/prefs')

    def set_preferences(self, prefs: Mapping[str, JSON_ro]) -> Mapping[str, Any]:
        """Update the current user's preferences.

        .. .PARAMETERS

        :param prefs:
            See the API docs for available preference settings:
            `<https://www.reddit.com/dev/api/#PATCH_api_v1_me_prefs>`_.
        :type prefs: `Mapping`\\[`str`, :obj:`~.types.JSON_ro`]

        .. .RETURNS

        :returns:
            The updated preferences, as you would get from :meth:`.get_preferences`.
        :rtype: `Mapping`\\[`str`, `Any`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        return self._client.request('PATCH', '/api/v1/me/prefs', json=prefs)

    def karma_breakdown(self) -> Sequence[KarmaBreakdownEntry]:
        """Get the current user's karma breakdown by subreddit.

        The entries are sorted in descending order by comment karma plus
        submission karma.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.karma_breakdown_entry.KarmaBreakdownEntry`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        root = self._client.request('GET', '/api/v1/me/karma')
        entries = root['data']
        return [load_karma_breakdown_entry(d) for d in entries]

    def trophies(self) -> Sequence[Trophy]:
        """Get a list of trophies for the current user.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.trophy.Trophy`]

        ..RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        root = self._client.request('GET', '/api/v1/me/trophies')
        kind_data = root['data']['trophies']
        return [load_trophy(d['data']) for d in kind_data]

    def list_friends(self) -> Sequence[UserRelationship]:
        """Get a list of friends.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.user_relationship.UserRelationship`]

        .. .RAISES

        :raises redditwarp.exceptions.OperationException:
            There is no user context.
        """
        try:
            root = self._client.request('GET', '/api/v1/me/friends')
        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        entries = root['data']['children']
        return [load_user_relationship(d) for d in entries]

    def get_friend(self, name: str) -> UserRelationship:
        """Get information about a specific 'friend'.

        This is an old reddit feature. See `<https://www.reddit.com/prefs/friends/>`_.

        .. .PARAMETERS

        :param `str` name:
            The name of a user.

        .. .RETURNS

        :rtype: :class:`~.models.user_relationship.UserRelationship`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NOT_FRIEND`:
                You are not friends with the specified user.
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
        """
        root = self._client.request('GET', f'/api/v1/me/friends/{name}')
        return load_user_relationship(root)

    def add_friend(self, name: str, note: Optional[str] = None) -> FriendRelationship:
        """Create or update a friend relationship.

        Also use this function to add or update a note.
        Note: making a note requires Reddit Premium.

        .. .PARAMETERS

        :param `str` name:
            The name of a user.
        :param `Optional[str]` note:
            Add or update a note.

            Using this parameter requires Reddit Premium, otherwise a
            `GOLD_REQUIRED` API error will occur.

        .. .RETURNS

        :returns:
            The updated user object on success.
        :rtype: :class:`~.models.user_relationship.FriendRelationship`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
            + `GOLD_REQUIRED`:
                You tried to add a note but you don't have Reddit Premium.
            + `NO_TEXT`:
                An empty string was specified for `note`.
        """
        json_data = {} if note is None else {'note': note}
        root = self._client.request('PUT', f'/api/v1/me/friends/{name}', json=json_data)
        return load_friend_relationship(root)

    def remove_friend(self, name: str) -> None:
        """Remove a friend.

        .. .PARAMETERS

        :param `str` name:
            The name of a user.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `NOT_FRIEND`:
                The user specified is not a friend.
        """
        self._client.request('DELETE', f'/api/v1/me/friends/{name}')

    def list_blocked_users(self) -> Sequence[UserRelationship]:
        """Get a list of blocked users.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.user_relationship.UserRelationship`]

        .. .RAISES

        :raises redditwarp.exceptions.OperationException:
            There is no user context.
        """
        try:
            root = self._client.request('GET', '/prefs/blocked')

        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        entries = root['data']['children']
        return [load_user_relationship(d) for d in entries]

    def block_user_by_id(self, idn: int) -> None:
        """Block a user by ID.

        .. .PARAMETERS

        :param `int` idn:
            The ID of the user to block.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
               - The username or user ID given doesn't exist.
               - You tried to block yourself.
        """
        self._client.request('POST', '/api/block_user', data={'account_id': to_base36(idn)})

    def block_user_by_name(self, name: str) -> None:
        """Block a user by name.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises:
            (Same as in :meth:`.block_user_by_id`.)
        """
        self._client.request('POST', '/api/block_user', data={'name': name})

    def unblock_user_by_target_id(self, target_id: int, agent_id: int) -> None:
        """Unblock a user by ID.

        .. .PARAMETERS

        :param `int` target_id:
            The user ID in which to unblock.
        :param `int` agent_id:
            Your user account's ID.

            The endpoint needs this information for some dumb reason.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                The target username or target user ID doesn't exist.
        """
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_id),
            'id': 't2_' + to_base36(target_id),
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def unblock_user_by_target_name(self, target_name: str, agent_id: int) -> None:
        """Unblock a user by name.

        Behaves similarly to :meth:`.unblock_user_by_target_id`.

        .. .PARAMETERS

        :param `str` target_name:
            The username in which to unblock.
        :param `int` agent_id:
            Your user account's ID.

            The endpoint needs this information for some dumb reason.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises:
            See :meth:`.unblock_user_by_target_id`.
        """
        data = {
            'type': 'enemy',
            'container': 't2_' + to_base36(agent_id),
            'name': target_name,
        }
        self._client.request('POST', '/api/unfriend', data=data)

    def list_trusted_users(self) -> Sequence[UserRelationship]:
        """Get a list of trusted users.

        Behaves similarly to :meth:`.blocked`.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.user_relationship.UserRelationship`]

        .. .RAISES

        :raises:
            See :meth:`.blocked`.
        """
        try:
            root = self._client.request('GET', '/prefs/trusted')

        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        entries = root['data']['children']
        return [load_user_relationship(d) for d in entries]

    def add_trusted_user(self, name: str) -> None:
        """Add a user to your trusted users list.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CANT_WHITELIST_AN_ENEMY`:
                The specified user is on your blocked list.
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
        """
        self._client.request('POST', '/api/add_whitelisted', params={'name': name})

    def remove_trusted_user(self, name: str) -> None:
        """Remove a user from your trusted users list.

        .. .PARAMETERS

        :param `str` name:
            The target user name.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        self._client.request('POST', '/api/remove_whitelisted', params={'name': name})

    def get_blocked_and_trusted_users(self) -> tuple[Sequence[UserRelationship], Sequence[UserRelationship]]:
        """Return the blocked and trusted user lists in one call.

        Behaves similarly to :meth:`.blocked`.

        .. .RETURNS

        :returns:
            A tuple of two lists:
            the first list contains blocked users,
            the second list contains trusted's users.
        :rtype: `tuple`\\[`Sequence`\\[:class:`~.models.user_relationship.UserRelationship`], `Sequence`\\[:class:`~.models.user_relationship.UserRelationship`]]

        .. .RAISES

        :raises:
            See :meth:`.blocked`.
        """
        try:
            root = self._client.request('GET', '/prefs/messaging')

        except http_exceptions.StatusCodeException as e:
            if e.status_code == 302:
                raise exceptions.OperationException('no user context')
            raise
        if isinstance(root, str):
            raise exceptions.OperationException('no user context')

        blocked_entries = root[0]['data']['children']
        trusted_entries = root[1]['data']['children']
        return (
            [load_user_relationship(d) for d in blocked_entries],
            [load_user_relationship(d) for d in trusted_entries],
        )
