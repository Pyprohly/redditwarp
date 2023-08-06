
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, IO, Mapping, Union, TypeVar
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission, TextPost
    from ...models.comment_ASYNC import Comment
    from ...types import JSON_ro

import os.path as op
from functools import cached_property
import json

from ...model_loaders.submission_ASYNC import load_submission, load_text_post
from ...models.submission_media_upload_lease import SubmissionMediaUploadLease
from ...model_loaders.submission_media_upload_lease import load_submission_media_upload_lease
from ...http.util.guess_filename_mimetype import guess_filename_mimetype
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_async_iterator import CallChunkCallingAsyncIterator
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.submission_async1 import SubmissionSearchAsyncPaginator, SubmissionDuplicatesAsyncPaginator
from ...model_loaders.comment_ASYNC import load_comment
from .fetch_ASYNC import Fetch
from .get_ASYNC import Get
from .create.ASYNC import Create

_YIntOrStr = TypeVar('_YIntOrStr', int, str)


class SubmissionProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch: Fetch = Fetch(self, client)
        ("""
            Fetch a submission.

            .. .PARAMETERS

            :param `Union[int, str]` idy:
                Submission ID.

            .. .RETURNS

            :rtype: :class:`~.models.submission_ASYNC.Submission`

            .. .RAISES

            :raises redditwarp.exceptions.NoResultException:
                The target was not found.
            """)
        self.get: Get = Get(client)
        ("""
            Get a submission.

            .. .PARAMETERS

            :param `Union[int, str]` idy:
                Submission ID.

            .. .RETURNS

            :rtype: `Optional`\\[:class:`~.models.submission_ASYNC.Submission`]
            """)
        self.create: Create = Create(client)
        ("""
            Create a submission.
            """)

    def bulk_fetch(self, ids: Iterable[_YIntOrStr]) -> CallChunkChainingAsyncIterator[Submission]:
        """Bulk fetch submissions.

        Any ID not found will be ignored.

        .. .PARAMETERS

        :param `Iterable[_YIntOrStr]` ids:
            Submission IDs.

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_chaining_async_iterator.CallChunkChainingAsyncIterator`\\[:class:`~.models.submission_ASYNC.Submission`]
        """
        async def mass_fetch(ids: Sequence[_YIntOrStr]) -> Sequence[Submission]:
            # https://github.com/python/mypy/issues/4134
            id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in ids)  # type: ignore[arg-type]
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = await self._client.request('GET', '/api/info', params={'id': ids_str})
            # https://github.com/python/mypy/issues/13408
            return [load_submission(i['data'], self._client) for i in root['data']['children']]  # type: ignore[return-value]

        return CallChunkChainingAsyncIterator(AsyncCallChunk[Sequence[_YIntOrStr], Sequence[Submission]](mass_fetch, chunk) for chunk in chunked(ids, 100))

    async def reply(self, idy: Union[int, str], body: Union[str, Mapping[str, JSON_ro]]) -> Comment:
        """Comment on a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param body:
            Either markdown or richtext.
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]

        .. .RETURNS

        :rtype: :class:`~.models.comment_ASYNC.Comment`

        .. .RAISES

        :(raises):
            Same as comment :meth:`~.siteprocs.comment.SYNC.CommentProcedures.reply`
            but for submissions.
        """
        def g() -> Iterable[tuple[str, str]]:
            id36 = x if isinstance((x := idy), str) else to_base36(x)
            yield ('thing_id', 't3_' + id36)
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/comment', files=dict(g()))
        return load_comment(result, self._client)

    class MediaUploading:
        def __init__(self, outer: SubmissionProcedures) -> None:
            self._client = outer._client

        async def __call__(self,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubmissionMediaUploadLease:
            return await self.upload(file, filepath=filepath, timeout=timeout)

        async def obtain_upload_lease(self,
            *,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> SubmissionMediaUploadLease:
            if mimetype is None:
                mimetype = guess_filename_mimetype(filepath)
            result = await self._client.request('POST', '/api/media/asset',
                    data={'filepath': filepath, 'mimetype': mimetype})
            return load_submission_media_upload_lease(result)

        async def deposit_file(self,
            file: IO[bytes],
            upload_lease: SubmissionMediaUploadLease,
            *,
            timeout: float = 1000,
        ) -> None:
            resp = await self._client.http.request('POST', upload_lease.endpoint,
                    data=upload_lease.fields, files={'file': file}, timeout=timeout)
            resp.ensure_successful_status()

        async def upload(self,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubmissionMediaUploadLease:
            if filepath is None:
                filepath = op.basename(getattr(file, 'name', ''))
                if not filepath:
                    raise ValueError("the `filepath` parameter must be explicitly specified if the file object has no `name` attribute.")
            upload_lease = await self.obtain_upload_lease(filepath=filepath)
            await self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

    media_uploading: cached_property[MediaUploading] = cached_property(MediaUploading)

    async def edit_text_post_body(self, idy: Union[int, str], body: Union[str, Mapping[str, JSON_ro]]) -> TextPost:
        """Edit the body text of a text post.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param body:
            Either markdown or richtext.
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]

        .. .RETURNS

        :rtype: :class:`~.models.submission_ASYNC.TextPost`

        .. .RAISES

        :raises:
            Same as comment :meth:`~.siteprocs.comment.SYNC.CommentProcedures.edit_body`
            but for submissions.
        """
        def g() -> Iterable[tuple[str, str]]:
            id36 = x if isinstance((x := idy), str) else to_base36(x)
            yield ('thing_id', 't3_' + id36)
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/editusertext', files=dict(g()))
        return load_text_post(result, self._client)

    async def delete(self, idy: Union[int, str]) -> None:
        """Delete a submission.

        If the target doesn't exist or isn't valid, nothing happens.

        When a submission is deleted it's text content (if a text post)
        will be set to "`[deleted]`" and the submission will be unlisted
        from its subreddit. Users can still otherwise view and reply to
        deleted to submissions if they have a direct link to it.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/del', data=data)

    async def lock(self, idy: Union[int, str]) -> None:
        """Lock a submission.

        Nothing happens if the target is already locked.

        .. hint::
           Locking prevents a submission/comment from receiving new comments.
           A locked submission is unable to receive any new comments.
           Locking a comment only stops direct comments, but
           existing child comments can still receive replies.

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
                The target doesn't exist or you don't have permission to lock it.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/lock', data=data)

    async def unlock(self, idy: Union[int, str]) -> None:
        """Unlock a submission.

        Behaves similarly to :meth:`.lock`.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises:
            Similar to :meth:`.lock`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/unlock', data=data)

    async def vote(self, idy: Union[int, str], direction: int) -> None:
        """Cast a vote on a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `int` direction:
            Either: `1` (upvote), `0` unvote, `-1` downvote.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The target could not be found.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'dir': str(direction),
        }
        await self._client.request('POST', '/api/vote', data=data)

    async def save(self, idy: Union[int, str], category: Optional[str] = None) -> None:
        """Save a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `Optional[str]` category:
            A category/label.

            Requires Reddit Premium. Ignored if no Reddit Premium.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The category name specified was invalid.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        if category is not None:
            data['category'] = category
        await self._client.request('POST', '/api/save', data=data)

    async def unsave(self, idy: Union[int, str]) -> None:
        """Save a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/unsave', data=data)

    async def hide(self, idy: Union[int, str]) -> None:
        """Hide a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                The target was not found.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/hide', data=data)

    async def unhide(self, idy: Union[int, str]) -> None:
        """Unhide a submission.

        See :meth:`.hide`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/unhide', data=data)

    def bulk_hide(self, ids: Iterable[_YIntOrStr]) -> CallChunkCallingAsyncIterator[None]:
        """Bulk hide submissions.

        If *any* of the list of submission IDs don't exist then the endpoint will
        return a HTTP 400 status error and none of the submissions will be hidden.
        This can be annoying since if the list is long it can be hard to tell which
        ID is the culprit.

        .. .PARAMETERS

        :param `Iterable[_YIntOrStr]` ids:

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_calling_async_iterator.CallChunkCallingAsyncIterator`\\[`None`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                If any of the IDs were not found.
        """
        # https://github.com/python/mypy/issues/13408
        async def mass_hide(ids: Sequence[_YIntOrStr]) -> None:  # type: ignore[return]
            # https://github.com/python/mypy/issues/4134
            id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in ids)  # type: ignore[arg-type]
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            await self._client.request('POST', '/api/hide', data={'id': ids_str})

        return CallChunkCallingAsyncIterator(AsyncCallChunk[Sequence[_YIntOrStr], None](mass_hide, chunk) for chunk in chunked(ids, 300))

    def bulk_unhide(self, ids: Iterable[_YIntOrStr]) -> CallChunkCallingAsyncIterator[None]:
        """Bulk hide submissions.

        See :meth:`.bulk_hide`.
        """
        # https://github.com/python/mypy/issues/13408
        async def mass_unhide(ids: Sequence[_YIntOrStr]) -> None:  # type: ignore[return]
            # https://github.com/python/mypy/issues/4134
            id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in ids)  # type: ignore[arg-type]
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            await self._client.request('POST', '/api/unhide', data={'id': ids_str})

        return CallChunkCallingAsyncIterator(AsyncCallChunk[Sequence[_YIntOrStr], None](mass_unhide, chunk) for chunk in chunked(ids, 300))

    async def mark_nsfw(self, idy: Union[int, str]) -> None:
        """Mark a submission as NSFW.

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
                You do not have permission to mark the target.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/marknsfw', data=data)

    async def unmark_nsfw(self, idy: Union[int, str]) -> None:
        """Unmark a submission as NSFW.

        See :meth:`.mark_nsfw`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/unmarknsfw', data=data)

    async def mark_spoiler(self, idy: Union[int, str]) -> None:
        """Mark a submission as spoiler.

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
                You do not have permission to mark the target.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/spoiler', data=data)

    async def unmark_spoiler(self, idy: Union[int, str]) -> None:
        """Unmark a submission as spoiler.

        See :meth:`.mark_spoiler`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/unspoiler', data=data)

    async def distinguish(self, idy: Union[int, str]) -> Submission:
        """Distinguish a submission.

        .. hint::

           Distinguishing decoratates the author's name by
           giving it a different color and putting a sigil beside it.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :returns: The target submission.
        :rtype: :class:`~.models.submission_ASYNC.Submission`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission to distinguish the target.
            + `404`:
                The target could not be found.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'how': 'yes',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    async def undistinguish(self, idy: Union[int, str]) -> Submission:
        """Undistinguish a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :returns: The target submission.
        :rtype: :class:`~.models.submission_ASYNC.Submission`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
            + `404`:
                The target could not be found.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'how': 'no',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    async def sticky(self, idy: Union[int, str], slot: Optional[int] = None) -> None:
        """Set a submission as sticky in its subreddit.

        .. hint::
           Stickied posts are shown at the top of the subreddit in the default 'Hot' listing.

        In a subreddit, there can be at most 2 sticked posts at a time.

        When stickying the `slot` parameter indicates which of the two positions the
        new post should occupy. If there is a sticked post in the slot specified by `slot`,
        it will be replaced. Otherwise the post will be placed in the bottom-most slot.
        If the number specified by `slot` is outside the valid range it will be clamped within range.

        Stickying a post that is already stickied causes a 409 (Conflict) HTTP error.
        Unstickying a post that isn't stickied does nothing.

        .. note::
           You cannot reorder sticky posts directly. You must unsticky and re-sticky them.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `Optional[int]` slot:
            Which sticky slot to use.

            If not specified, the bottom-most slot will be used if available.
            If the sticky list is at maximum length, the bottom-most slot will
            be replaced with the new post.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission to sticky that post.
            + `409`:
                The post is already stickied.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'state': '1',
        }
        if slot is not None:
            data['num'] = str(slot)
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def unsticky(self, idy: Union[int, str]) -> None:
        """Unsticky a submission.

        See :meth:`.sticky`.

        Unstickying a post that isn't stickied does nothing.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'state': '0',
        }
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def pin_to_profile(self, idy: Union[int, str], slot: Optional[int] = None) -> None:
        """Pin a post you created to your user profile.

        .. hint::
           Pinned posts show up at the start of the
           'Overview', or 'Submitted' (old UI) / 'POSTS' (redesign UI)
           user profile listings.

        A user can have at most 4 pinned posts at a time.

        The rules for the num parameter are the same as in subreddit stickying.
        See :meth:`.sticky`. However, there are differences when the slot number
        is unspecified. See the `slot` parameter description.

        .. note::
           This feature uses the same endpoint as :meth:`.sticky` but there are
           stark differences in insertion behaviour when `slot` is not specified.

           To summarise:

           * When subreddit stickying: the post will be placed at the **bottom** of the list.
             If the list is full then the bottom-most post will be **replaced**.
           * When user profile pinning: the post will be placed at the **top** of the list.
             If the list is full then the bottom-most post will be **evicted**.

        Pinning a post that is already pinned causes a 409 (Conflict) HTTP error.
        Unpinning a post that isn't pinned does nothing.

        .. note::
           You cannot reorder pinned posts directly. You must unpin and re-pin them.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `Optional[int]` slot:
            Which pin slot to use.

            If `slot` is not specified, the new post is inserted at the top of the list.
            If the list is at maximum length, the least recently pinned post will be evicted.
            It acts like a queue.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission to pin that post.
            + `409`:
                The post is already pinned.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'to_profile': '1',
            'state': '1',
        }
        if slot is not None:
            data['num'] = str(slot)
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def unpin_from_profile(self, idy: Union[int, str]) -> None:
        """Unpin a submission from your user profile.

        See :meth:`.pin_to_profile`.

        Unpinning a post that isn't pinned does nothing.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'to_profile': '1',
            'state': '0',
        }
        await self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    async def set_contest_mode(self, idy: Union[int, str], state: bool) -> None:
        """Set or unset 'contest mode' for a submission's comments.

        .. hint::

            In contest mode, vote counts are hidden and comments are displayed
            in a random order.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `bool` state:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The specified ID was not found.
               - You do not have permission to modify the target.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'state': '01'[state],
        }
        await self._client.request('POST', '/api/set_contest_mode', data=data)

    async def set_suggested_sort(self, idy: Union[int, str], sort: str) -> None:
        """Set or unset the suggested sort for a submission's comments.

        .. hint::

           When set, users will see comments in the suggested sort order by default.
           They can still manually change back to their preferred sort if they choose.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `str` sort:
            Either: `confidence`, `top`, `new`, `controversial`,
            `old`, `random`, `qa`, `live`, `blank`.

            If not specified or an unknown value, the suggested sort will be unset.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The specified ID was not found.
               - You do not have permission to modify the target.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'sort': sort,
        }
        await self._client.request('POST', '/api/set_suggested_sort', data=data)

    async def enable_reply_notifications(self, idy: Union[int, str]) -> None:
        """Enable inbox reply notifications for a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'state': '1'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def disable_reply_notifications(self, idy: Union[int, str]) -> None:
        """Disable inbox reply notifications for a submission.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'state': '0'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def set_event_time(self, idy: Union[int, str],
            event_start: Optional[str] = None,
            event_end: Optional[str] = None,
            event_tz: Optional[str] = None) -> None:
        """Add or modify event times on a submission.

        Specify only `event_start` to change only the starting date.
        The same cannot be done for `event_end`, a 500 HTTP error will occur.

        If both `event_start` and `event_end` are specified then the `event_start` must be before
        `event_end` in time, otherwise a `MIN_EVENT_TIME` API error is returned.
        It is possible however to make a second request specifying only `event_start` to modify
        the start date so that `event_start` is after `event_end`. If this happens then the time
        difference can be longer than 7 days.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `Optional[str]` event_start:
            A datetime ISO 8601 string. E.g. `2018-09-11T12:00:00`.
        :param `Optional[str]` event_end:
            A datetime ISO 8601 string.
        :param `Optional[str]` event_tz:
            A timezone. E.g., `America/Los_Angeles`.

            If not specified, effectively defaults to `UTC`.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `BAD_TIME`:
               - The value specified for `event_start` or `event_end` is in a bad format.
               - The date string specified for `event_start` or `event_end` is in the past.

               Note that this error will always indicate `event_start` is wrong even if
               it's `event_end` that needs fixing.
            + `MIN_EVENT_TIME`:
                The value specified for `event_tz` is invalid.
            + `MAX_EVENT_TIME`:
                The event can't be longer than 7 days.
            + `INVALID_TIMEZONE`:
                The value specified for `event_tz` is invalid.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `500`:
                The `event_start` parameter was not specified.
        """
        def g() -> Iterable[tuple[str, str]]:
            id36 = x if isinstance((x := idy), str) else to_base36(x)
            yield ('id', 't3_' + id36)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        await self._client.request('POST', '/api/event_post_time', data=dict(g()))

    async def follow_event(self, idy: Union[int, str]) -> None:
        """Follow a post event.

        .. hint::
           Followers receive a push notification when the event starts.

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
                The target submission is not an event.
            + `404`:
                The target submission does not exist.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'fullname': 't3_' + id36,
            'follow': '1',
        }
        await self._client.request('POST', '/api/follow_post', data=data)

    async def unfollow_event(self, idy: Union[int, str]) -> None:
        """Unfollow a post event.

        See :meth:`.follow_event`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'fullname': 't3_' + id36,
            'follow': '0',
        }
        await self._client.request('POST', '/api/follow_post', data=data)

    async def approve(self, idy: Union[int, str]) -> None:
        """Approve a submission.

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
               You do not have permission.

               - The target specified does not exist.
               - The target belongs to a subreddit you do not have permission over.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36}
        await self._client.request('POST', '/api/approve', data=data)

    async def remove(self, idy: Union[int, str]) -> None:
        """Remove a submission.

        This is a moderator action.

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
               You do not have permission.

               - The target specified does not exist.
               - The target belongs to a subreddit you do not have permission over.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'spam': '0',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def remove_spam(self, idy: Union[int, str]) -> None:
        """Remove as spam.

        See :meth:`.remove`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {
            'id': 't3_' + id36,
            'spam': '1',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def ignore_reports(self, idy: Union[int, str]) -> None:
        """Ignore reports on a submission.

        .. hint::
           If you ignore reports, you won't receive notifications and the
           ignored thing will be absent from moderation listings.

        Nothing happens if the target is already ignored.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
            Submission ID.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The target specified does not exist.
               - The target belongs to a subreddit you do not have permission over.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        await self._client.request('POST', '/api/ignore_reports', data={'id': 't3_' + id36})

    async def unignore_reports(self, idy: Union[int, str]) -> None:
        """Unignore reports on a submission.

        Nothing happens if the target is already unignored.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
            Submission ID.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The target specified does not exist.
               - The target belongs to a subreddit you do not have permission over.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        await self._client.request('POST', '/api/unignore_reports', data={'id': 't3_' + id36})

    async def snooze_reports(self, idy: Union[int, str], reason: str) -> None:
        """Ignore a custom report reason in a subreddit for 7 days.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
            Submission ID.
        :param `str` reason:
            The custom report reason to snooze.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The target specified does not exist.
               - The target belongs to a subreddit you do not have permission over.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36, 'reason': reason}
        await self._client.request('POST', '/api/snooze_reports', data=data)

    async def unsnooze_reports(self, idy: Union[int, str], reason: str) -> None:
        """Unsnooze a custom report.

        See :meth:`.snooze_reports`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'id': 't3_' + id36, 'reason': reason}
        await self._client.request('POST', '/api/unsnooze_reports', data=data)

    async def apply_removal_reason(self,
            idy: Union[int, str],
            reason_id: Optional[str] = None,
            note: Optional[str] = None) -> None:
        """Set a removal reason on a removed submission.

        If the target is not a removed submission, nothing happens.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
            Submission ID.
        :param `Optional[int]` reason_id:
            A removal reason ID.
        :param `Optional[str]` note:
            A note.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `JSON_MISSING_KEY`:
                Empty strings or null values were specified for both
                `reason_id` and `note` at the same time.
            + `NO_THING_ID`:
                The given target ID is not valid.
            + `INVALID_ID`:
                The reason ID is invalid.
            + `MUST_BE_PRESENT`:
                The subreddit specified does not exist.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The target specified does not belong to a subreddit you moderate.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        json_data = {'item_ids': ['t3_' + id36], 'reason_id': reason_id, 'mod_note': note}
        await self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    async def send_removal_comment(self,
            idy: Union[int, str],
            title: str,
            message: str,
            *,
            exposed: bool = False,
            locked: bool = False) -> Comment:
        """Send a removal comment.

        Sends a removal reason comment to a user for a removed submission of theirs.

        This action can be performed multiple times.
        (The UI does not normally let you do this.)

        Unlike :meth:`.apply_removal_reason`, the target you specify must be a
        removed item otherwise an `INVALID_ID` API error is produced.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
            ID of a removed submission.
        :param `str` title:
            A title.

            This is ultimately unused for removal comments, but a non-empty
            string must be specified or you'll get a `NO_TEXT` API error.

            The UI sends the title of the selected removal reason.
        :param `str` message:
            A message for the comment body.

            Can be an empty string. This is interesting because you can't
            normally create comments with empty bodies.
        :param `bool` exposed:
            If false (default), the comment will be created by a special
            moderator named `u/{subreddit}_ModTeam`.

            If true, the comment is created by the current user.
        :param `bool` locked:
            Lock the newly created comment.

        .. .RETURNS

        :returns: The newly created comment.
        :rtype: :class:`~.models.comment_ASYNC.Comment`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
                The value for the `title` parameter was empty.
            + `INVALID_ID`:
               - The target specified doesn't exist or is invalid.
               - The target specified is not a removed item.

            + `MUST_BE_PRESENT`:
                The subreddit specified does not exist.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - The target specified does not belong to a subreddit you moderate.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        json_data = {
            'type': 'public' + ('' if exposed else '_as_subreddit'),
            'item_id': ['t3_' + id36],
            'title': title,
            'message': message,
            'lock_comment': '01'[locked],
        }
        root = await self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)
        return load_comment(root, self._client)

    async def send_removal_message(self,
            idy: Union[int, str],
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        """Send a removal message.

        Behaves similarly to :meth:`.send_removal_comment`.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
            ID of a removed comment.
        :param `str` title:
            A title.

            A non-empty string must be specified or you'll get a `NO_TEXT` API error.

            The UI sends the title of the selected removal reason.
        :param `str` message:
            A message for the comment body.

            Can be an empty string.
        :param `bool` exposed:
            If false (default), the comment will be send on behalf of the subreddit.

            If true, the comment is sent by the current user.

        .. .RETURNS

        :returns: `None`

        .. .RAISES

        :(raises): See :meth:`.send_removal_comment`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        json_data = {
            'type': 'private' + ('_exposed' if exposed else ''),
            'item_id': ['t3_' + id36],
            'title': title,
            'message': message,
        }
        await self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)

    def search(self, sr: str, query: str, amount: Optional[int] = None, *,
        sort: str = 'relevance', time: str = 'all',
    ) -> ImpartedPaginatorChainingAsyncIterator[SubmissionSearchAsyncPaginator, Submission]:
        """Search for submissions.

        .. .PARAMETERS

        :param `str` sr:
            A subreddit name.

            Use an empty string to search all of Reddit.
        :param `str` query:
            A search query.
        :param `Optional[int]` amount:
            The number of items to retrieve.
        :param `str` sort:
            Either: `relevance`, `hot`, `top`, `new`, or `comments`.

            Default: `relevance`.
        :param `str` time:
            Either: `all`, `hour`, `day`, `week`, `month`, `year`.

            Default: `all`.

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`\\[:class:`~.pagination.paginators.submission_async1.SubmissionSearchAsyncPaginator`, :class:`~.models.submission_ASYNC.Submission`]
        """
        url = '/search'
        if sr:
            url = f'/r/{sr}/search'
        p = SubmissionSearchAsyncPaginator(
                self._client, url,
                params={'q': query, 'restrict_sr': '1'},
                    sort=sort, time=time)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def duplicates(self, target: Union[int, str], amount: Optional[int] = None, *,
        sort: str = 'num_comments',
    ) -> ImpartedPaginatorChainingAsyncIterator[SubmissionDuplicatesAsyncPaginator, Submission]:
        """Get crossposts for a submission.

        .. .PARAMETERS

        :param `Union[int, str]` target:
            Submission ID.
        :param `Optional[int]` amount:
            The number of items to retrieve.
        :param `str` sort:
            Either `num_comments` or `new`.

            Default: `num_comments`.

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`\\[:class:`~.pagination.paginators.submission_async1.SubmissionDuplicatesAsyncPaginator`, :class:`~.models.submission_ASYNC.Submission`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                Fetching some submissions resulted in a 403.
            + `404`:
                The target submission could not be found.
        """
        id36 = x if isinstance((x := target), str) else to_base36(x)
        p = SubmissionDuplicatesAsyncPaginator(self._client, f'/duplicates/{id36}', sort=sort)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
