
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Any, Mapping, Union, TypeVar
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import LooseComment
    from ...models.subreddit_rules import SubredditRules
    from ...types import JSON_ro

from ...models.subreddit_SYNC import Subreddit, InaccessibleSubreddit
from ...model_loaders.subreddit_SYNC import load_subreddit, load_potentially_inaccessible_subreddit
from ...model_loaders.subreddit_rules import load_subreddit_rules
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.listing.comment_listing_paginator import LooseCommentListingPaginator
from ...pagination.paginators.subreddit_sync1 import SubredditSearchPaginator
from ... import exceptions
from ... import http
from .pull_SYNC import Pull
from .pulls_SYNC import Pulls

_YIntOrStr = TypeVar('_YIntOrStr', int, str)

class SubredditProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull: Pull = Pull(client)
        ("""
            Pull subreddit submissions.
            """)
        self.pulls: Pulls = Pulls(client)
        ("""
            Pull subreddits.
            """)

    def get(self, idy: Union[int, str]) -> Optional[Subreddit]:
        """Get information about a potentially inaccessible subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :returns:
            * `None` if the subreddit does not exist, or the subreddit is private or banned.
            * :class:`~.models.subreddit_SYNC.Subreddit`
        :rtype: `Optional`\\[:class:`~.models.subreddit_SYNC.Subreddit`]
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        v = self.get_potentially_inaccessible(id36)
        if isinstance(v, Subreddit):
            return v
        return None

    def fetch(self, idy: Union[int, str]) -> Subreddit:
        """Fetch information about a potentially inaccessible subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: :class:`~.models.subreddit_SYNC.Subreddit`

        .. .RAISES

        :raises redditwarp.exceptions.OperationException:
           - The target subreddit is was not found.
           - The target subreddit is private or banned.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        v = self.fetch_potentially_inaccessible(id36)
        if isinstance(v, Subreddit):
            return v
        if isinstance(v, InaccessibleSubreddit):
            raise exceptions.RejectedResultException
        raise Exception

    def get_by_name(self, name: str) -> Optional[Subreddit]:
        """Return information about a subreddit by name.

        Returns `None` when the target subreddit is private or banned, or
        if the specified subreddit name contained invalid characters, or
        you specified the name of a special subreddit:
        `all`, `popular`, `friends`, `mod`.

        .. .PARAMETERS

        :param `str` name:
            Subreddit name.

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.subreddit_SYNC.Subreddit`]
        """
        try:
            root = self._client.request('GET', f'/r/{name}/about')
        except exceptions.RedditError as e:
            if e.label.lower() in ('private', 'banned'):
                return None
            raise
        except http.exceptions.StatusCodeException as e:
            if e.status_code in (302, 404):
                return None
            raise
        if root['kind'] == 'Listing':
            return None
        return load_subreddit(root['data'], self._client)

    def fetch_by_name(self, name: str) -> Subreddit:
        """Return information about a subreddit by name.

        Behaves similarly to :meth:`.get_by_name`.

        .. .PARAMETERS

        :param `str` name:
            Subreddit name.

        .. .RETURNS

        :rtype: :class:`~.models.subreddit_SYNC.Subreddit`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `private`:
                The target subreddit is private.
            + `banned`:
                The target subreddit is banned.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
               - The subreddit does not exist.

            + `404`:
               - You specified the name of a special subreddit: `all`, `popular`, `friends`, `mod`.
               - The specified subreddit name was too long or contained invalid characters.
        """
        root = self._client.request('GET', f'/r/{name}/about')
        if root['kind'] == 'Listing':
            raise exceptions.NoResultException('target not found')
        return load_subreddit(root['data'], self._client)

    def get_potentially_inaccessible(self, idy: Union[int, str]) -> Optional[object]:
        """Get information about a potentially inaccessible subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :returns:
            * :class:`~.models.subreddit_SYNC.InaccessibleSubreddit` if the subreddit is private or banned.
            * `None` if the subreddit does not exist.
            * :class:`~.models.subreddit_SYNC.Subreddit`
        :rtype: `Optional`\\[`object`]
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        full_id36 = 't5_' + id36
        root = self._client.request('GET', '/api/info', params={'id': full_id36})
        if children := root['data']['children']:
            return load_potentially_inaccessible_subreddit(children[0]['data'], self._client)
        return None

    def fetch_potentially_inaccessible(self, idy: Union[int, str]) -> object:
        """Fetch information about a potentially inaccessible subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :returns:
            * :class:`~.models.subreddit_SYNC.InaccessibleSubreddit` if the subreddit is private or banned.
            * `None` if the subreddit does not exist.
            * :class:`~.models.subreddit_SYNC.Subreddit`
        :rtype: `Optional`\\[`object`]

        .. .RAISES

        :raises redditwarp.exceptions.NoResultException:
            The target subreddit is was not found.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        v = self.get_potentially_inaccessible(id36)
        if v is None:
            raise exceptions.NoResultException('target not found')
        return v

    def get_potentially_inaccessible_by_name(self, name: str) -> Optional[object]:
        """Get information about a potentially inacessible subreddit.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :returns:
            * :class:`~.models.subreddit_SYNC.InaccessibleSubreddit` if the subreddit is private or banned.
            * `None` if the subreddit does not exist.
            * :class:`~.models.subreddit_SYNC.Subreddit`
        :rtype: `Optional`\\[`object`]
        """
        root = self._client.request('GET', '/api/info', params={'sr_name': name})
        if children := root['data']['children']:
            return load_potentially_inaccessible_subreddit(children[0]['data'], self._client)
        return None

    def fetch_potentially_inaccessible_by_name(self, name: str) -> object:
        """Fetch information about a potentially inacessible subreddit.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :returns:
            * :class:`~.models.subreddit_SYNC.InaccessibleSubreddit` if the subreddit is private or banned.
            * `None` if the subreddit does not exist.
            * :class:`~.models.subreddit_SYNC.Subreddit`
        :rtype: `object`

        .. .RAISES

        :raises redditwarp.exceptions.NoResultException:
            The target subreddit is was not found.
        """
        v = self.get_potentially_inaccessible_by_name(name)
        if v is None:
            raise exceptions.NoResultException('target not found')
        return v

    def bulk_fetch_potentially_inaccessible(self, ids: Iterable[_YIntOrStr]) -> CallChunkChainingIterator[object]:
        """Bulk fetch information about a potentially inacessible subreddits, by ID.

        Any ID not found will be ignored.

        .. .PARAMETERS

        :param `Iterable[_YIntOrStr]` ids:

        .. .RETURNS

        :returns:
            Iterator of:

            * :class:`~.models.subreddit_SYNC.InaccessibleSubreddit` if the subreddit is private or banned.
            * `None` if the subreddit does not exist.
            * :class:`~.models.subreddit_SYNC.Subreddit`
        :rtype: :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[`object`]
        """
        def mass_fetch(ids: Sequence[_YIntOrStr]) -> Sequence[object]:
            # https://github.com/python/mypy/issues/4134
            id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in ids)  # type: ignore[arg-type]
            full_id36s = map('t5_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(CallChunk[Sequence[_YIntOrStr], Sequence[object]](mass_fetch, chunk) for chunk in chunked(ids, 100))

    def bulk_fetch_potentially_inaccessible_by_name(self, names: Iterable[str]) -> CallChunkChainingIterator[object]:
        """Bulk fetch information about a potentially inacessible subreddits, by name.

        Any name not found will be ignored.

        .. .PARAMETERS

        :param `Iterable[int]` ids:

        .. .RETURNS

        :returns:
            Iterator of:

            * :class:`~.models.subreddit_SYNC.InaccessibleSubreddit` if the subreddit is private or banned.
            * `None` if the subreddit does not exist.
            * :class:`~.models.subreddit_SYNC.Subreddit`
        :rtype: :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[`object`]
        """
        def mass_fetch(names: Sequence[str]) -> Sequence[object]:
            root = self._client.request('GET', '/api/info', params={'sr_name': ','.join(names)})
            return [load_potentially_inaccessible_subreddit(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(CallChunk(mass_fetch, chunk) for chunk in chunked(names, 100))

    def pull_new_comments(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[LooseCommentListingPaginator, LooseComment]:
        """Pull new comments from a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `Optional[int]` amount:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.listing.comment_listing_paginator.LooseCommentListingPaginator`, :class:`~.models.comment_SYNC.LooseComment`]
        """
        p = LooseCommentListingPaginator(self._client, f'/r/{sr}/comments')
        return ImpartedPaginatorChainingIterator(p, amount)

    def get_settings(self, sr: str) -> Mapping[str, Any]:
        """Get the settings of a subreddit.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `Mapping`\\[`str`, `Any`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
                The specified subreddit does not exist.
            + `404`:
               - There is no user context.
               - You don't have permission to view this subreddit's settings.
        """
        root = self._client.request('GET', f'/r/{sr}/about/edit')
        if root['kind'] != 'subreddit_settings':
            raise exceptions.NoResultException('target not found')
        return root['data']

    def update_settings(self, idy: Union[int, str], settings: Mapping[str, JSON_ro]) -> None:
        """Update a subreddit's settings.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param settings:
        :type settings: `Mapping`\\[`str`, :class:`~.types.JSON_ro`]

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `SUBREDDIT_REQUIRED`:
                The specified subreddit does not exist.
            + `MOD_REQUIRED`:
                The current user is not a moderator of the subreddit.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        full_id36 = 't5_' + id36
        json: Mapping[str, JSON_ro] = {**settings, 'sr': full_id36}
        self._client.request('PATCH', '/api/v1/subreddit/update_settings', json=json)

    def subscribe_by_id(self, idy: Union[int, str]) -> None:
        """Subscribe to a subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The specified subreddit could not be accessed.
            + `404`:
                The specified subreddit does not exist.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        full_id36 = 't5_' + id36
        self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr': full_id36})

    def subscribe_by_name(self, name: str) -> None:
        """Subscribe to a subreddit.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The specified subreddit could not be accessed.
               - The specified subreddit was a special name such as `popular`, `all`, or `random`.

            + `404`:
                The specified subreddit does not exist.
        """
        self._client.request('POST', '/api/subscribe', data={'action': 'sub', 'sr_name': name})

    def unsubscribe_by_id(self, idy: Union[int, str]) -> None:
        """Unsubscribe from a subreddit.

        Behaves similarly to :meth:`.subscribe_by_id`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        full_id36 = 't5_' + id36
        self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr': full_id36})

    def unsubscribe_by_name(self, name: str) -> None:
        """Unsubscribe from a subreddit.

        Behaves similarly to :meth:`.subscribe_by_name`.
        """
        self._client.request('POST', '/api/subscribe', data={'action': 'unsub', 'sr_name': name})

    def get_rules(self, sr: str) -> SubredditRules:
        r"""Get a subreddit's rules.

        Example::

           rules = client.p.subreddit.get_rules(SR)
           for i, rule in enumerate(rules, 1):
               print(f"{i}. {rule.short_name}\n{rule.description}\n")

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: :class:`~.models.subreddit_rules.SubredditRules`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The specified subreddit could not be accessed.
        """
        root = self._client.request('GET', f'/r/{sr}/about/rules')
        if 'rules' not in root:
            raise exceptions.NoResultException('target not found')
        return load_subreddit_rules(root)

    def get_post_requirements(self, sr: str) -> Mapping[str, Any]:
        """Get the post requirement settings of a subreddit.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `Mapping`\\[`str`, `Any`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `SUBREDDIT_NOEXIST`:
                The specified subreddit does not exist.
            + `SUBREDDIT_NO_ACCESS`:
                The specified subreddit is private or banned.
        """
        return self._client.request('GET', f'/api/v1/{sr}/post_requirements')

    def search(self, query: str, amount: Optional[int] = None,
            ) -> ImpartedPaginatorChainingIterator[SubredditSearchPaginator, Subreddit]:
        """Search subreddits by name or description.

        .. .PARAMETERS

        :param `str` query:
        :param `Optional[int]` amount:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.subreddit_sync1.SubredditSearchPaginator`, :class:`~.models.subreddit_SYNC.Subreddit`]
        """
        if not query:
            raise ValueError('query cannot be empty')
        p = SubredditSearchPaginator(self._client, '/subreddits/search', query)
        return ImpartedPaginatorChainingIterator(p, amount)

    def search_names(self, name: str) -> Sequence[str]:
        """List subreddit names that begin with a query string.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :rtype: `Sequence`\\[`str`]
        """
        root = self._client.request('GET', '/api/search_reddit_names', params={'query': name})
        return root['names']

    def exists(self, name: str) -> bool:
        """Check whether a subreddit name exists.

        An empty string returns true.

        .. .PARAMETERS

        :param `str` name:

        .. .RETURNS

        :rtype: `bool`
        """
        try:
            self._client.request('GET', '/api/search_reddit_names', params={'query': name, 'exact': '1'})
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return False
            raise
        return True

    def get_similar_subreddits(self, idy: Union[int, str], n: Optional[int] = None) -> Sequence[Subreddit]:
        """Get a list of similar subreddits.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `Optional[int]` n:
            The maximum number of entries to return.

            Effective default: 10.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.subreddit_SYNC.Subreddit`]
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        params = {'sr_fullnames': 't5_' + id36}
        if n is not None:
            params['max_recs'] = str(n)
        root = self._client.request('GET', '/api/similar_subreddits', params=params)
        return [load_subreddit(d['data'], client=self._client) for d in root['data']['children']]
