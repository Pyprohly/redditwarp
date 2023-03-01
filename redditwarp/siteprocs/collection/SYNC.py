
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_collection_SYNC import SubmissionCollectionInfo, SubmissionCollection

from functools import cached_property

from ...model_loaders.submission_collection_SYNC import load_submission_collection_info, load_submission_collection
from ...util.base_conversion import to_base36
from .create_SYNC import Create
from .add_post_SYNC import AddPost
from .remove_post_SYNC import RemovePost
from .reorder_SYNC import Reorder

class CollectionProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.create: Create = Create(client)
        ("""
            Create a collection.

            Returns the newly created collection.

            .. .PARAMETERS

            :param `int` sr_id:
                Subreddit ID.
            :param `str` title:
                A string no longer than 300 characters.
            :param `Optional[str]` description:
                A string no longer than 500 characters.
            :param `Optional[str]` display_layout:
                Either `TIMELINE` or `GALLERY`.

                Default is `TIMELINE`.

            .. .RETURNS

            :rtype: :class:`~.models.submission_collection_SYNC.SubmissionCollection`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `USER_REQUIRED`:
                    There is no user context.
                + `SUBREDDIT_NOEXIST`:
                    The specified subreddit (`sr_id`) does not exist.
                + `NO_TEXT`:
                    The specified `title` was empty.
                + `TOO_LONG`:
                   - The specified `title` was longer than 300 characters.
                   - The specified `description` was longer than 500 characters.

                + `INVALID_OPTION`:
                    The value specified for `display_layout` is not valid.

                    The options are case-sensitive.
            """)
        self.add_post: AddPost = AddPost(client)
        ("""
            Add a submission to a collection.

            Collections have a capacity of 100 posts. Attempting to add to a full
            collection will result in an `INVALID_COLLECTION_UPDATE` API error.

            .. .PARAMETERS

            :param `str` uuid:
            :param `int` submission_id:

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `USER_REQUIRED`:
                    There is no user context.
                + `NO_TEXT`:
                    The specified `uuid` was empty.
                + `TOO_SHORT`:
                    The specified `uuid` was under 36 characters.
                + `TOO_LONG`:
                   - The specified `uuid` was over 36 characters.
                   - The specified `description` was longer than 500 characters.

                + `INVALID_COLLECTION_UPDATE`:
                   - The specified `uuid` does not exist.
                   - The submission specified by `submission_id` already exists in
                     the collection.
                   - The submission specified by `submission_id` does not match
                     the collection's subreddit.
                   - The collection is full (it contains 100 posts).

            :raises redditwarp.http.exceptions.StatusCodeException:
                + `404`:
                    The submission specified by `submission_id` does not exist.
                + `500`:
                    The value specified by `uuid` is not a valid UUID.
            """)
        self.remove_post: RemovePost = RemovePost(client)
        ("""
            Remove a submission from a collection.

            .. .PARAMETERS

            :param `str` uuid:
            :param `int` submission_id:

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `USER_REQUIRED`:
                    There is no user context.
                + `NO_TEXT`:
                    The specified `uuid` was empty.
                + `TOO_SHORT`:
                    The specified `uuid` was under 36 characters.
                + `TOO_LONG`:
                   - The specified `uuid` was over 36 characters.
                   - The specified `description` was longer than 500 characters.

                + `INVALID_COLLECTION_UPDATE`:
                   - The specified `uuid` does not exist.
                   - The submission specified by `submission_id` does not exist in
                     the collection.

            :raises redditwarp.http.exceptions.StatusCodeException:
                + `404`:
                   The submission specified by `submission_id` does not exist.
                + `500`:
                   The value specified by `uuid` is not a valid UUID.
            """)
        self.reorder: Reorder = Reorder(client)
        ("""
            Reorder posts in a collection.

            An API error is returned (`INVALID_COLLECTION_UPDATE`) if an ID in
            the given list is not found in the collection.

            If only a subset of the IDs in the collection are specified then those
            submissions will be moved to the top of the collection in the order specified.
            The rest are moved down, maintaining their order.

            .. .PARAMETERS

            :param `str` uuid:
            :param `Sequence[int]` submission_ids:

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `USER_REQUIRED`:
                    There is no user context.
                + `INVALID_COLLECTION_UPDATE`:
                    One of the IDs specified in the `submission_ids` list does not
                    exist in the collection.
            :raises redditwarp.http.exceptions.StatusCodeException:
                + `404`:
                   - The specified `uuid` was empty.
                   - The specified `uuid` is invalid.
                   - The specified `uuid` does not exist.
            """)

    def get_full(self, uuid: str) -> Optional[SubmissionCollection]:
        """Get a collection, including its submissions.

        .. .PARAMETERS

        :param `str` uuid:

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.submission_collection_SYNC.SubmissionCollection`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `NO_TEXT`:
                The specified `uuid` was empty.
            + `TOO_SHORT`:
                The specified `uuid` was under 36 characters.
            + `TOO_LONG`:
                The specified `uuid` was over 36 characters.
        """
        params = {'collection_id': uuid}
        root = self._client.request('GET', '/api/v1/collections/collection', params=params)
        if len(root) < 3:
            return None
        return load_submission_collection(root, self._client)

    def get_info(self, uuid: str) -> Optional[SubmissionCollectionInfo]:
        """Get a collection, excluding its submissions.

        .. .PARAMETERS

        :param `str` uuid:

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.submission_collection_SYNC.SubmissionCollectionInfo`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `NO_TEXT`:
                The specified `uuid` was empty.
            + `TOO_SHORT`:
                The specified `uuid` was under 36 characters.
            + `TOO_LONG`:
                The specified `uuid` was over 36 characters.
        """
        params = {'collection_id': uuid, 'include_links': '0'}
        root = self._client.request('GET', '/api/v1/collections/collection', params=params)
        if len(root) < 3:
            return None
        return load_submission_collection_info(root, self._client)

    class GetSubredditCollectionsInfo:
        def __init__(self, outer: CollectionProcedures) -> None:
            self._client = outer._client

        def __call__(self, id: int) -> Sequence[SubmissionCollectionInfo]:
            id36 = to_base36(id)
            return self.by_id36(id36)

        def by_id36(self, id36: str) -> Sequence[SubmissionCollectionInfo]:
            params = {'sr_fullname': 't5_' + id36}
            root = self._client.request('GET', '/api/v1/collections/subreddit_collections', params=params)
            return [load_submission_collection_info(d, self._client) for d in root]

    get_subreddit_collections_info: cached_property[GetSubredditCollectionsInfo] = \
            cached_property(GetSubredditCollectionsInfo)
    ("""
        Get a list of collections' details from the subreddit.

        .. .PARAMETERS

        :param `int` id:
            Subreddit ID.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.submission_collection_SYNC.SubmissionCollectionInfo`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `SUBREDDIT_NOEXIST`:
                The specified subreddit could not be found.
        """)

    def delete(self, uuid: str) -> None:
        """Delete a collection.

        .. .PARAMETERS

        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
                The specified `uuid` was empty.
            + `TOO_SHORT`:
                The specified `uuid` was under 36 characters.
            + `TOO_LONG`:
                The specified `uuid` was over 36 characters.
            + `INVALID_COLLECTION_ID`:
                The specified does not exist.
        """
        params = {'collection_id': uuid}
        self._client.request('POST', '/api/v1/collections/delete_collection', params=params)

    def set_title(self, uuid: str, title: str) -> None:
        """Update a collection's title.

        .. .PARAMETERS

        :param `str` uuid:
        :param `str` title:
            New title for the collection, up to 300 characters long.

            It should not be an empty string.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
               - The specified `uuid` was empty.
               - The specified `title` was empty.

            + `TOO_SHORT`:
                The specified `uuid` was under 36 characters.
            + `TOO_LONG`:
               - The specified `uuid` was over 36 characters.
               - The specified `title` was over 300 characters.

            + `INVALID_COLLECTION_ID`:
                The specified `uuid` does not exist.
        """
        params = {'collection_id': uuid, 'title': title}
        self._client.request('POST', '/api/v1/collections/update_collection_title', params=params)

    def set_description(self, uuid: str, desc: str) -> None:
        """Update a collection's description.

        .. .PARAMETERS

        :param `str` uuid:
        :param `str` title:
            New description for the collection, up to 500 characters long.

            Can be an empty string.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
               - The specified `uuid` was empty.
               - The specified `title` was empty.

            + `TOO_SHORT`:
                The specified `uuid` was under 36 characters.
            + `TOO_LONG`:
               - The specified `uuid` was over 36 characters.
               - The specified `description` was over 500 characters.

            + `INVALID_COLLECTION_ID`:
                The specified `uuid` does not exist.
        """
        params = {'collection_id': uuid, 'description': desc}
        self._client.request('POST', '/api/v1/collections/update_collection_description', params=params)

    def set_display_layout(self, uuid: str, layout: Optional[str]) -> None:
        """Update a collection's display layout.

        .. .PARAMETERS

        :param `str` uuid:
        :param `Optional[str]` layout:
            Either `TIMELINE` or `GALLERY`.

            Case-sensitive.

            If not specified or an empty string, the `display_layout` field on the collection
            object will be set to null, which is treated the same as `TIMELINE`.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
                The specified `uuid` was empty.
            + `TOO_SHORT`:
                The specified `uuid` was under 36 characters.
            + `TOO_LONG`:
                The specified `uuid` was over 36 characters.
            + `INVALID_COLLECTION_ID`:
                The specified `uuid` does not exist.
            + `INVALID_OPTION`:
                The value specified for `display_layout` is not valid.

                The options are case-sensitive.
        """
        params = {'collection_id': uuid}
        if layout is not None:
            params['display_layout'] = layout
        self._client.request('POST', '/api/v1/collections/update_collection_display_layout', params=params)

    def follow(self, uuid: str) -> None:
        """Follow a collection.

        This actually has a similar effect to
        :meth:`~.siteprocs.submission.SYNC.SubmissionProcedures.follow_event`.
        When you follow a collection, all submissions in the collection will be followed,
        *even if there is no event information* on any of the posts.

        When a new submission is added to a followed collection, the submission is
        automatically followed. If any of the individual submissions are unfollowed via
        :meth:`~.siteprocs.submission.SYNC.SubmissionProcedures.unfollow_event`
        then the whole collection and all of its submissions are unfollowed,
        having the same effect as :meth:`.unfollow`.

        To tell if a collection is followed, check if one of its submissions is::

           coll = client.p.collection.get_full('84359211-be58-4c98-87cd-26bc10c59fb3')
           if coll is None:
               raise Exception
           followed = any(subm.me.is_following_event for subm in coll)
           print(followed)

        .. .PARAMETERS

        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
                The specified `uuid` was empty.
            + `TOO_SHORT`:
                The specified `uuid` was under 36 characters.
            + `TOO_LONG`:
                The specified `uuid` was over 36 characters.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `500`:
                The specified `uuid` does not exist.
        """
        params = {'follow': '1', 'collection_id': uuid}
        self._client.request('POST', '/api/v1/collections/follow_collection', params=params)

    def unfollow(self, uuid: str) -> None:
        """Unfollow a collection.

        .. .PARAMETERS

        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises):
            (Same as :meth:`.follow`.)
        """
        params = {'follow': '0', 'collection_id': uuid}
        self._client.request('POST', '/api/v1/collections/follow_collection', params=params)
