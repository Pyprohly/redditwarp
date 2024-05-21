
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Union, TypeVar, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.user_ASYNC import User
    from ...models.moderated_subreddit import ModeratedSubreddit

from .pull_ASYNC import Pull
from .pull_subreddits_ASYNC import PullSubreddits
from ...model_loaders.user_ASYNC import load_user, load_potentially_suspended_user
from ...model_loaders.moderated_subreddit import load_moderated_subreddit
from ... import http
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.user.async1 import UserSearchAsyncPaginator
from ...exceptions import RejectedResultException
from ...models.user_summary import UserSummary
from ...model_loaders.user_summary import load_user_summary
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk

_YIntOrStr = TypeVar('_YIntOrStr', int, str)

class UserProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull: Pull = Pull(client)
        ("""
            Pull submissions and comments associated with a user.
            """)
        self.pull_subreddits: PullSubreddits = PullSubreddits(client)
        ("""
            Get user subreddits.
            """)

    async def get_by_name(self, name: str) -> Optional[User]:
        """Get information about a user by name.

        Returns `None` if the specified user was not found,
        or is a suspended account.

        .. .PARAMETERS

        :param `str` name:
            User name.

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.user_ASYNC.User`]
        """
        try:
            root = await self._client.request('GET', f'/user/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        obj_data = root['data']
        if obj_data.get('is_suspended', False):
            return None
        return load_user(obj_data, self._client)

    async def fetch_by_name(self, name: str) -> User:
        """Fetch information about a user by name.

        .. .PARAMETERS

        :param `str` name:
            User name.

        .. .RETURNS

        :rtype: :class:`~.models.user_ASYNC.User`

        .. .RAISES

        :raises redditwarp.exceptions.RejectedResultException:
            The specified user account is suspended.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified user was not found.
        """
        root = await self._client.request('GET', f'/user/{name}/about')
        obj_data = root['data']
        if obj_data.get('is_suspended', False):
            raise RejectedResultException('user is suspended')
        return load_user(obj_data, self._client)

    async def get_potentially_suspended_by_name(self, name: str) -> Optional[object]:
        """Get information about a potentially suspended user, by name.

        Returns `None` if the specified user was not found.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :returns:
            * :class:`~.models.user_ASYNC.User` if the user exists.
            * :class:`~.models.user_ASYNC.SuspendedUser` if the user is suspended.
            * `None` if the user was not found.
        :rtype: `Optional`\\[`object`]
        """
        try:
            root = await self._client.request('GET', f'/user/{name}/about')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return load_potentially_suspended_user(root['data'], self._client)

    async def fetch_potentially_suspended_by_name(self, name: str) -> object:
        """Fetch information about a potentially suspended user, by name.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :returns:
            * :class:`~.models.user_ASYNC.User` if the user exists.
            * :class:`~.models.user_ASYNC.SuspendedUser` if the user is suspended.
        :rtype: `object`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified user was not found.
        """
        root = await self._client.request('GET', f'/user/{name}/about')
        return load_potentially_suspended_user(root['data'], self._client)

    async def get_user_summary(self, idy: Union[int, str]) -> Optional[UserSummary]:
        """Get a partial user object by ID.

        .. .PARAMETERS

        :param `Union[int, str]` idn:

        .. .RETURNS

        :returns:
            * :class:`~.models.user_summary.UserSummary`
            * `None` if the user was not found.
        :rtype: `Optional`\\[:class:`~.models.user_summary.UserSummary`]
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        full_id36 = 't2_' + id36
        try:
            root = await self._client.request('GET', '/api/user_data_by_account_ids',
                    params={'ids': full_id36})
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        obj_data = root[full_id36]
        return load_user_summary(obj_data, id36)

    def bulk_fetch_user_summary(self, ids: Iterable[_YIntOrStr]) -> CallChunkChainingAsyncIterator[UserSummary]:
        """
        Bulk fetch partial user objects, by ID.

        Any ID that can't be resolved will be ignored.
        Duplicate IDs in a batch will be ignored.

        .. .PARAMETERS

        :param `Iterable[_YIntOrStr]` ids:

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_chaining_async_iterator.CallChunkChainingAsyncIterator`\\[:class:`~.models.user_summary.UserSummary`]
        """
        async def mass_fetch_by_id(ids: Sequence[_YIntOrStr]) -> Sequence[UserSummary]:
            # https://github.com/python/mypy/issues/4134
            id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in ids)  # type: ignore[arg-type]
            full_id36s = map('t2_'.__add__, id36s)
            ids_str = ','.join(full_id36s)

            try:
                root = await self._client.request('GET', '/api/user_data_by_account_ids', params={'ids': ids_str})
            except http.exceptions.StatusCodeException as e:
                if e.status_code == 404:
                    return []
                raise
            return [load_user_summary(v, k) for k, v in root.items()]

        return CallChunkChainingAsyncIterator(AsyncCallChunk[Sequence[_YIntOrStr], Sequence[UserSummary]](mass_fetch_by_id, idfs) for idfs in chunked(ids, 100))

    async def moderating(self, name: str) -> Sequence[ModeratedSubreddit]:
        """Get a list of partial subreddit objects the target user is a moderator of.

        This endpoint isn't very reliable on users with big lists.

        The specified user's own user subreddit won't be returned, but any other user
        subreddit they moderate will be.

        .. seealso::

           :meth:`p.account.pull_subreddits.moderating() <.pull_subreddits_ASYNC.PullSubreddits.moderating>`
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
        root = await self._client.request('GET', f'/user/{name}/moderated_subreddits')
        if not root:
            return ()
        return [load_moderated_subreddit(d) for d in root['data']]

    def search(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingAsyncIterator[UserSearchAsyncPaginator, User]:
        """Search users by name or description.

        .. .PARAMETERS

        :param `str` query:
        :param `Optional[int]` amount:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`\\[:class:`~.pagination.paginators.user.async1.UserSearchAsyncPaginator`, :class:`~.models.user_ASYNC.User`]
        """
        p = UserSearchAsyncPaginator(self._client, '/users/search', query)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def exists(self, name: str) -> bool:
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
        return not await self._client.request('GET', '/api/username_available', params={'user': name})
