
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_SYNC import User
    from ...models.moderated_subreddit import ModeratedSubreddit

from .get_user_summary_SYNC import GetUserSummary
from .bulk_fetch_user_summary_SYNC import BulkFetchUserSummary
from .pull_SYNC import Pull
from .pull_subreddits_SYNC import PullSubreddits
from ...model_loaders.user_SYNC import load_user, load_potentially_suspended_user
from ...model_loaders.moderated_subreddit import load_moderated_subreddit
from ... import http
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.user.sync1 import UserSearchPaginator
from ...exceptions import RejectedResultException

class UserProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.get_user_summary: GetUserSummary = GetUserSummary(client)
        ("""
            Get a partial user object by ID.

            .. .PARAMETERS

            :param `int` idn:

            .. .RETURNS

            :returns:
                * :class:`~.models.user_summary.UserSummary`
                * `None` if the user was not found.
            :rtype: `Optional`\\[:class:`~.models.user_summary.UserSummary`]
            """)
        self.bulk_fetch_user_summary: BulkFetchUserSummary = BulkFetchUserSummary(client)
        ("""
            Bulk fetch partial user objects, by ID.

            Any ID that can't be resolved will be ignored.
            Duplicate IDs in a batch will be ignored.

            .. .PARAMETERS

            :param `Iterable[int]` ids:

            .. .RETURNS

            :rtype: :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[:class:`~.models.user_summary.UserSummary`]
            """)
        self.pull: Pull = Pull(client)
        ("""
            Pull submissions and comments associated with a user.
            """)
        self.pull_subreddits: PullSubreddits = PullSubreddits(client)
        ("""
            Get user subreddits.
            """)

    def get_by_name(self, name: str) -> Optional[User]:
        """Get information about a user by name.

        Returns `None` if the specified user was not found,
        or is a suspended account.

        .. .PARAMETERS

        :param `str` name:
            User name.

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.user_SYNC.User`]
        """
        try:
            root = self._client.request('GET', f'/user/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        obj_data = root['data']
        if obj_data.get('is_suspended', False):
            return None
        return load_user(obj_data, self._client)

    def fetch_by_name(self, name: str) -> User:
        """Fetch information about a user by name.

        .. .PARAMETERS

        :param `str` name:
            User name.

        .. .RETURNS

        :rtype: :class:`~.models.user_SYNC.User`

        .. .RAISES

        :raises redditwarp.exceptions.RejectedResultException:
            The specified user account is suspended.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified user was not found.
        """
        root = self._client.request('GET', f'/user/{name}/about')
        obj_data = root['data']
        if obj_data.get('is_suspended', False):
            raise RejectedResultException('user is suspended')
        return load_user(obj_data, self._client)

    def get_potentially_suspended_by_name(self, name: str) -> Optional[object]:
        """Get information about a potentially suspended user, by name.

        Returns `None` if the specified user was not found.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :returns:
            * :class:`~.models.user_SYNC.User` if the user exists.
            * :class:`~.models.user_SYNC.SuspendedUser` if the user is suspended.
            * `None` if the user was not found.
        :rtype: `Optional`\\[`object`]
        """
        try:
            root = self._client.request('GET', f'/user/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return load_potentially_suspended_user(root['data'], self._client)

    def fetch_potentially_suspended_by_name(self, name: str) -> object:
        """Fetch information about a potentially suspended user, by name.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :returns:
            * :class:`~.models.user_SYNC.User` if the user exists.
            * :class:`~.models.user_SYNC.SuspendedUser` if the user is suspended.
        :rtype: `object`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified user was not found.
        """
        root = self._client.request('GET', f'/user/{name}/about')
        return load_potentially_suspended_user(root['data'], self._client)

    def moderating(self, name: str) -> Sequence[ModeratedSubreddit]:
        """Get a list of partial subreddit objects the target user is a moderator of.

        This endpoint isn't very reliable on users with big lists.

        The specified user's own user subreddit won't be returned, but any other user
        subreddit they moderate will be.

        .. seealso::

           :meth:`p.account.pull_subreddits.moderating() <.pull_subreddits_SYNC.PullSubreddits.moderating>`
              For obtaining a list of the current user's moderated subreddits.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.moderated_subreddit.ModeratedSubreddit`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified user was not found.
        """
        root = self._client.request('GET', f'/user/{name}/moderated_subreddits')
        if not root:
            return ()
        return [load_moderated_subreddit(d) for d in root['data']]

    def search(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[UserSearchPaginator, User]:
        """Search users by name or description.

        .. .PARAMETERS

        :param `str` query:
        :param `Optional[int]` amount:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.user.sync1.UserSearchPaginator`, :class:`~.models.user_SYNC.User`]
        """
        p = UserSearchPaginator(self._client, '/users/search', query)
        return ImpartedPaginatorChainingIterator(p, amount)

    def exists(self, name: str) -> bool:
        """Check whether a user name exists.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :rtype: `bool`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `BAD_USERNAME`:
                * The specified parameter is empty.
                * The specified username contains illegal characters.
        """
        return not self._client.request('GET', '/api/username_available', params={'user': name})
