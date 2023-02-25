
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Any, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.custom_feed_SYNC import CustomFeed

import json

from ...model_loaders.custom_feed_SYNC import load_custom_feed
from ... import exceptions
from ... import http
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_iterator import CallChunkCallingIterator
from ...iterators.call_chunk import CallChunk

class CustomFeedProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._json_encoder = encoder = json.JSONEncoder()
        self._json_encode = encoder.encode

    def fetch(self, user: str, feed: str) -> CustomFeed:
        """Fetch a custom feed resource.

        .. .PARAMETERS

        :param `str` user:
            A user name.
        :param `str` feed:
            Custom feed name.

        .. .RETURNS

        :rtype: :class:`~.models.custom_feed_SYNC.CustomFeed`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `MULTI_NOT_FOUND`:
                The custom feed specified doesn't exist or you don't have permission to view it.
        """
        root = self._client.request('GET', f'/api/multi/user/{user}/m/{feed}')
        return load_custom_feed(root['data'], self._client)

    def get(self, user: str, feed: str) -> Optional[CustomFeed]:
        """Get a custom feed resource.

        Returns `None` if the custom feed was not found.

        .. .PARAMETERS

        :param `str` user:
            A user name.
        :param `str` feed:
            Custom feed name.

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.custom_feed_SYNC.CustomFeed`]
        """
        try:
            root = self._client.request('GET', f'/api/multi/user/{user}/m/{feed}')
        except exceptions.RedditError as e:
            if e.label == 'MULTI_NOT_FOUND':
                return None
            raise
        return load_custom_feed(root['data'], self._client)

    def retrieve_mine(self) -> Sequence[CustomFeed]:
        """Fetch a list of custom feeds curated by the current user.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.custom_feed_SYNC.CustomFeed`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        result = self._client.request('GET', '/api/multi/mine')
        return [load_custom_feed(d['data'], self._client) for d in result]

    def retrieve(self, user: str) -> Sequence[CustomFeed]:
        """Fetch a list of custom feeds curated by a given user.

        .. .PARAMETERS

        :param `Optional[str]` user:
            The user in which to retrieve custom feeds for.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.custom_feed_SYNC.CustomFeed`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
        """
        result = self._client.request('GET', f'/api/multi/user/{user}')
        return [load_custom_feed(d['data'], self._client) for d in result]

    def create(self,
        user: str,
        feed: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        subreddit_names: Sequence[str] = (),
        exposed: bool = False,
    ) -> CustomFeed:
        """Create a custom feed.

        .. .PARAMETERS

        :param `str` user:
        :param `str` feed:
        :param `Optional[str]` title:
            Title.

            No longer than 50 characters.

            If null, feed name is used.
        :param `Optional[str]` description:
            Markdown description text.

            Defaults to empty string.
        :param `Sequence[str]` subreddit_names:
            A list of subreddit names to include in the custom feed.
        :param `bool` exposed:
            Whether the custom feed is publicly accessible.

        .. .RETURNS

        :returns: The newly created custom feed.
        :rtype: :class:`~.models.custom_feed_SYNC.CustomFeed`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `MULTI_CANNOT_EDIT`:
               - The username specified does not exist.
               - You don't have permission to create a custom feed there.

            + `MULTI_EXISTS`:
                The custom feed already exists.
            + `TOO_LONG`:
                The text specified by `title` is over 50 characters.
        """
        json_data: dict[str, Any] = {}
        if title is not None:
            json_data['display_name'] = title
        if description is not None:
            json_data['description_md'] = description
        if subreddit_names:
            json_data['subreddits'] = {'name': nm for nm in subreddit_names}
        if not exposed:
            json_data['visibility'] = 'public'

        json_str = self._json_encode(json_data)
        root = self._client.request('POST', f'/api/multi/user/{user}/m/{feed}', data={'model': json_str})
        return load_custom_feed(root['data'], self._client)

    def put(self,
        user: str,
        feed: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        subreddit_names: Sequence[str] = (),
        exposed: bool = False,
    ) -> CustomFeed:
        """Create or update a custom feed.

        Behaves similar to :meth:`.create`.

        .. .PARAMETERS

        :param `str` user:
        :param `str` feed:
        :param `Optional[str]` title:
        :param `Optional[str]` description:
        :param `Sequence[str]` subreddit_names:
        :param `bool` exposed:

        .. .RETURNS

        :returns: The created/updated created custom feed.
        :rtype: :class:`~.models.custom_feed_SYNC.CustomFeed`

        .. .RAISES

        :(raises): Similar to :meth:`.create`,
            but `RedditError('MULTI_EXISTS')` is not possible.
        """
        json_data: dict[str, Any] = {}
        if title is not None:
            json_data['display_name'] = title
        if description is not None:
            json_data['description_md'] = description
        if subreddit_names:
            json_data['subreddits'] = [{'name': nm} for nm in subreddit_names]
        if not exposed:
            json_data['visibility'] = 'public'

        json_str = self._json_encode(json_data)
        root = self._client.request('PUT', f'/api/multi/user/{user}/m/{feed}', data={'model': json_str})
        return load_custom_feed(root['data'], self._client)

    def delete(self, user: str, feed: str) -> None:
        """Delete a custom feed.

        .. .PARAMETERS

        :param `str` user:
        :param `str` feed:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `MULTI_NOT_FOUND`:
               - The custom feed name specified does not exist.
               - The username specified does not exist.

            + `MULTI_CANNOT_EDIT`:
                You don't have permission to delete the specified custom feed
                because it does not belong to you.
        """
        self._client.request('DELETE', f'/api/multi/user/{user}/m/{feed}')

    def copy(self, src_user: str, src_feed: str, dst_user: str, dst_feed: str, *,
            title: Optional[str] = None, description: Optional[str] = None) -> CustomFeed:
        """Copy a custom feed.

        The description for the new custom feed will be like "`copied from u/spez`" etc.
        unless overridden by the `description` parameter.

        .. .PARAMETERS

        :param `str` src_user:
        :param `str` src_feed:
        :param `str` dst_user:
        :param `str` dst_feed:

        .. .RETURNS

        :returns: The newly created custom feed.
        :rtype: :class:`~.models.custom_feed_SYNC.CustomFeed`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `MULTI_NOT_FOUND`:
                The source custom feed was not found.
            + `BAD_MULTI_PATH`:
                The destination path was not valid.
            + `MULTI_EXISTS`:
                The destination custom feed already exists.
            + `TOO_LONG`:
                The text specified by `title` is over 50 characters.
        """
        data = {
            'from': f'/user/{src_user}/m/{src_feed}',
            'to': f'/user/{dst_user}/m/{dst_feed}',
        }
        if title is not None:
            data['display_name'] = title
        if description is not None:
            data['description_md'] = description

        root = self._client.request('POST', '/api/multi/copy', data=data)
        return load_custom_feed(root['data'], self._client)

    def contains(self, user: str, feed: str, sr_name: str) -> bool:
        """Tell if a subreddit is in a custom feed.

        .. .PARAMETERS

        :param `str` user:
        :param `str` feed:
        :param `str` sr_name:
            Subreddit name.

        .. .RETURNS

        :rtype: `bool`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `MULTI_NOT_FOUND`:
                The custom feed does not exist.
        """
        try:
            self._client.request('GET', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}')
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 500:
                return False
            raise
        except exceptions.RedditError as e:
            if e.label == 'SUBREDDIT_NOEXIST':
                return False
            raise
        return True

    def add_item(self, user: str, feed: str, sr_name: str) -> None:
        """Add a subreddit to a custom feed.

        The `user` parameter does not have to match the current user's name!
        If the user name refers to a user that exists and the feed name you
        specify exists on that user, you'll get a `MULTI_CANNOT_EDIT` API error.
        If the username or feed name you specify doesn't exist, the custom feed
        will be created, seemingly under that user's name, but the custom feed
        will only be visible to you.

        If the specified feed name doesn't exist, it will be created.

        .. .PARAMETERS

        :param `str` user:
        :param `str` feed:
        :param `str` sr_name:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `SUBREDDIT_NOEXIST`:
                The specified subreddit does not exist.
            + `MULTI_CANNOT_EDIT`:
                The target custom feed exists and you don't have permission to add to it.
        """
        json_str = self._json_encode({"name": "abc"})
        self._client.request('PUT', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}', data={'model': json_str})

    def bulk_add_item(self, user: str, feed: str, sr_names: Iterable[str]) -> CallChunkCallingIterator[None]:
        """Bulk add subreddits to a custom feed.

        If any of the subreddit names in `sr_names` doesn't exist, the request will fail
        with a 500 HTTP error and none of the subreddits will be added.

        .. .PARAMETERS

        :param `str` user:
        :param `str` feed:
        :param `Iterable[str]` sr_names:

        .. .RETURNS

        :rtype: `~.iterators.call_chunk_calling_iterator.CallChunkCallingIterator`\\[`None`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `500`:
               - The specified username does not exist.
               - The specified custom feed name doesn't exist.
               - One of the subreddits specified in the `sr_names` list does not exist.
        """
        def mass_add_item(sr_names: Sequence[str]) -> None:
            data = {'path': f'/user/{user}/m/{feed}', 'sr_names': (','.join(sr_names))}
            self._client.request('POST', '/api/multi/add_srs_bulk', data=data)

        return CallChunkCallingIterator(CallChunk(mass_add_item, chunk) for chunk in chunked(sr_names, 300))

    def remove_item(self, user: str, feed: str, sr_name: str) -> None:
        """Remove a subreddit from a custom feed.

        .. .PARAMETERS

        :param `str` user:
        :param `str` feed:
        :param `str` sr_name:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `MULTI_NOT_FOUND`:
               - The specified username does not exist.
               - The specified custom feed name does not exist.
            + `MULTI_CANNOT_EDIT`:
                You don't have permission.
        """
        self._client.request('DELETE', f'/api/multi/user/{user}/m/{feed}/r/{sr_name}')
