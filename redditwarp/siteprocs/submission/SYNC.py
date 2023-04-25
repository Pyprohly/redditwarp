
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, IO, Mapping, Union
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_SYNC import Submission, TextPost
    from ...models.comment_SYNC import Comment
    from ...dtos.submission import GalleryItem
    from ...types import JSON_ro

import os.path as op
from functools import cached_property
import json

from ...model_loaders.submission_SYNC import load_submission, load_text_post
from ...models.submission_media_upload_lease import SubmissionMediaUploadLease
from ...model_loaders.submission_media_upload_lease import load_submission_media_upload_lease
from ...http.util.guess_filename_mimetype import guess_filename_mimetype
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_iterator import CallChunkCallingIterator
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.submission_sync1 import SubmissionSearchPaginator, SubmissionDuplicatesPaginator
from ...model_loaders.comment_SYNC import load_comment
from .fetch_SYNC import Fetch
from .get_SYNC import Get


class SubmissionProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch: Fetch = Fetch(self, client)
        ("""
            Fetch a submission.

            .. .PARAMETERS

            :param `int` idn:
                Submission ID.

            .. .RETURNS

            :rtype: :class:`~.models.submission_SYNC.Submission`

            .. .RAISES

            :raises redditwarp.exceptions.NoResultException:
                The target was not found.
            """)
        self.get: Get = Get(client)
        ("""
            Get a submission.

            .. .PARAMETERS

            :param `int` idn:
                Submission ID.

            .. .RETURNS

            :rtype: `Optional`\\[:class:`~.models.submission_SYNC.Submission`]
            """)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingIterator[Submission]:
        """Bulk fetch submissions.

        Any ID not found will be ignored.

        .. .PARAMETERS

        :param `Iterable[int]` ids:
            Submission IDs.

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[:class:`~.models.submission_SYNC.Submission`]
        """
        def mass_fetch(ids: Sequence[int]) -> Sequence[Submission]:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_submission(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(CallChunk(mass_fetch, chunk) for chunk in chunked(ids, 100))

    def reply(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> Comment:
        """Comment on a submission.

        .. .PARAMETERS

        :param `int` idn:
        :param body:
            Either markdown or richtext.
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]

        .. .RETURNS

        :rtype: :class:`~.models.comment_SYNC.Comment`

        .. .RAISES

        :(raises):
            Same as comment :meth:`~.siteprocs.comment.SYNC.CommentProcedures.reply`
            but for submissions.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't3_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = self._client.request('POST', '/api/comment', files=dict(g()))
        return load_comment(result, self._client)

    class MediaUploading:
        def __init__(self, outer: SubmissionProcedures) -> None:
            self._client = outer._client

        def __call__(self,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubmissionMediaUploadLease:
            return self.upload(file, filepath=filepath, timeout=timeout)

        def obtain_upload_lease(self,
            *,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> SubmissionMediaUploadLease:
            if mimetype is None:
                mimetype = guess_filename_mimetype(filepath)
            result = self._client.request('POST', '/api/media/asset',
                    data={'filepath': filepath, 'mimetype': mimetype})
            return load_submission_media_upload_lease(result)

        def deposit_file(self,
            file: IO[bytes],
            upload_lease: SubmissionMediaUploadLease,
            *,
            timeout: float = 1000,
        ) -> None:
            resp = self._client.http.request('POST', upload_lease.endpoint,
                    data=upload_lease.fields, files={'file': file}, timeout=timeout)
            resp.ensure_successful_status()

        def upload(self,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubmissionMediaUploadLease:
            if filepath is None:
                filepath = op.basename(getattr(file, 'name', ''))
                if not filepath:
                    raise ValueError("the `filepath` parameter must be explicitly specified if the file object has no `name` attribute.")
            upload_lease = self.obtain_upload_lease(filepath=filepath)
            self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

    media_uploading: cached_property[MediaUploading] = cached_property(MediaUploading)

    def create_text_post(self,
        sr: str,
        title: str,
        body: Union[str, Mapping[str, JSON_ro]],
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        """Create a text post.

        .. .PARAMETERS

        :param `str` sr:
            Name of the subreddit to submit the post to.
        :param `str` title:
            Title of the post.
        :param body:
            The body text of the post.

            Specify either markdown text or a richtext document.
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]
        :param `bool` reply_notifications:
            Receive inbox notifications for replies.
        :param `bool` spoiler:
            Mark as spoiler.
        :param `bool` nsfw:
            Mark as NSFW.
        :param `bool` oc:
            Mark as original content.
        :param `Optional[str]` collection_uuid:
            The UUID of a collection to add this post to a collection.
        :param `Optional[str]` flair_uuid:
            The UUID of a flair template to use.
        :param `Optional[str]` flair_text:
            Custom flair text.
        :param `Optional[str]` event_start:
            A datetime ISO 8601 string. E.g. `2018-09-11T12:00:00`.
        :param `Optional[str]` event_end:
            A datetime ISO 8601 string.
        :param `Optional[str]` event_tz:
            A timezone. E.g., `America/Los_Angeles`.

        .. .RETURNS

        :returns: The ID of the newly created post.
        :rtype: `int`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `BAD_SR_NAME`:
                An empty string was specified for `sr`.
            + `SUBREDDIT_NOEXIST`:
               - The specified subreddit does not exist.
               - The specified subreddit is invalid.

            + `SUBREDDIT_NOTALLOWED`:
               - The subreddit is restricted and you are not an approved user.
               - You are banned from the subreddit.
               - You are trying to submit an image or video post to a NSFW subreddit.

               Note, quarantined subreddits can be posted to even if you haven't
               yet opt-ed in to viewing its content.
            + `NO_TEXT`:
                The `title` parameter was not specified, was blank, or contained only whitespace.
            + `JSON_PARSE_ERROR`:
                Richtext was passed and it was not in the correct format.
            + `TOO_LONG`:
               - The `title` parameter must be under 300 characters.
               - The `body` parameter must be under 40000 characters.

            + `NO_SELFS`:
                The subreddit doesn't accept text posts.
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The target subreddit is private or banned.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'self')
            yield ('sr', sr)
            yield ('title', title)
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit', files=dict(g()))
        return int(root['json']['data']['id'], 36)

    def create_link_post(self,
        sr: str,
        title: str,
        link: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
        resubmit: bool = True,
    ) -> int:
        """Create a link post.

        Behaves similarly to :meth:`.create_text_post`.

        .. .PARAMETERS

        :(parameters): Similar to :meth:`.create_text_post`.

        :param `str` url:
            A URL.
        :param `bool` resubmit:
            When the "Restrict how often the same link can be posted" content control
            setting is enabled, if a link with the same URL has already been submitted
            then an `ALREADY_SUB` API error would be returned unless this field is true.

        .. .RETURNS

        :(returns): Similar to :meth:`.create_text_post`.

        .. .RAISES

        :(raises): Similar to :meth:`.create_text_post`.

        :raises redditwarp.exceptions.RedditError:
            + `NO_URL`:
                The `link` parameter was not specified, or the URL is invalid.
            + `ALREADY_SUB`:
                The given link has already been submitted to the subreddit.
                See parameter `resubmit`.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'link')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', link)
            if resubmit: yield ('resubmit', '1')
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit', data=dict(g()))
        return int(root['json']['data']['id'], 36)

    def create_image_post(self,
        sr: str,
        title: str,
        link: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> None:
        """Create an image post.

        Behaves similarly to :meth:`.create_text_post`.

        .. .PARAMETERS

        :(parameters): Similar to :meth:`.create_text_post`.

        :param `str` link:
            A URL to an image.

        .. .RETURNS

        :(returns): Similar to :meth:`.create_text_post`.

        .. .RAISES

        :(raises): Similar to :meth:`.create_text_post`.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'image')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', link)
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        self._client.request('POST', '/api/submit', data=dict(g()))

    def create_video_post(self,
        sr: str,
        title: str,
        link: str,
        thumbnail: str,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
        vgif: bool = False,
    ) -> None:
        """Create a video post.

        Behaves similarly to :meth:`.create_text_post`.

        .. .PARAMETERS

        :(parameters): Similar to :meth:`.create_text_post`.

        :param `str` link:
            A URL to a video.
        :param `str` thumbnail:
            A URL to an image to be used as a thumbnail for the video.
        :param `bool` vgif:
            Pass `True` to create a video GIF.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises): Similar to :meth:`.create_text_post`.

        :raises redditwarp.exceptions.RedditError:
            + `MISSING_VIDEO_URLS`:
                The `thumbnail` parameter was empty.
            + `NO_VIDEOS`:
                The subreddit does not accept video posts.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'video' + ('gif' if vgif else ''))
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', link)
            yield ('video_poster_url', thumbnail)
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        self._client.request('POST', '/api/submit', data=dict(g()))

    def create_gallery_post(self,
        sr: str,
        title: str,
        items: Sequence[GalleryItem],
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        """Create a gallery post.

        Behaves similarly to :meth:`.create_text_post`.

        .. .PARAMETERS

        :(parameters): Similar to :meth:`.create_text_post`.

        :param items:
            A list of gallery items.
        :type items: `Sequence`\\[:class:`~.dtos.submission.GalleryItem`]

        .. .RETURNS

        :(returns): Similar to :meth:`.create_text_post`.

        .. .RAISES

        :(raises): Similar to :meth:`.create_text_post`.
        """
        gallery_items: list[dict[str, str]] = [
            {
                'media_id': m.media_id,
                'caption': m.caption,
                'outbound_url': m.outbound_link,
            }
            for m in items
        ]

        def g() -> Iterable[tuple[str, JSON_ro]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('items', gallery_items)
            yield ('sendreplies', reply_notifications)
            if spoiler: yield ('spoiler', True)
            if nsfw: yield ('nsfw', True)
            if oc: yield ('original_content', True)
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit_gallery_post', json=dict(g()))
        return int(root['json']['data']['id'][3:], 36)

    def create_poll_post(self,
        sr: str,
        title: str,
        body: str,
        options: Sequence[str],
        duration: int,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        """Create a poll post.

        Behaves similarly to :meth:`.create_text_post`.

        .. .PARAMETERS

        :(parameters): Similar to :meth:`.create_text_post`.

        :param `str` body:
        :param `Sequence[str]` options:
        :param `int` duration:
            The number of days the poll runs for.

            Valid values are 1 to 7. If a number is specified outside
            this range it is clamped within range.

            The UI default is 3 days.

        .. .RETURNS

        :(returns): Similar to :meth:`.create_text_post`.

        .. .RAISES

        :(raises): Similar to :meth:`.create_text_post`.
        """
        def g() -> Iterable[tuple[str, JSON_ro]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('text', body)
            yield ('options', options)
            yield ('duration', duration)
            yield ('sendreplies', reply_notifications)
            if spoiler: yield ('spoiler', True)
            if nsfw: yield ('nsfw', True)
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit_poll_post', json=dict(g()))
        return int(root['json']['data']['id'][3:], 36)

    def create_crosspost(self,
        sr: str,
        title: str,
        idn: int,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        """Create a crosspost.

        Behaves similarly to :meth:`.create_text_post`.

        .. .PARAMETERS

        :(parameters): Similar to :meth:`.create_text_post`.

        :param `int` idn:
            The ID of a submission.

        .. .RETURNS

        :(returns): Similar to :meth:`.create_text_post`.

        .. .RAISES

        :(raises): Similar to :meth:`.create_text_post`.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'self')
            yield ('sr', sr)
            yield ('title', title)
            yield ('crosspost_parent', 't3_' + to_base36(idn))
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        root = self._client.request('POST', '/api/submit', data=dict(g()))
        return int(root['json']['data']['id'], 36)

    def create_cross_post(self,
        sr: str,
        title: str,
        idn: int,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> int:
        """Alias for :meth:`.create_crosspost`.

        .. versionadded:: 1.1.0
        """
        return self.create_crosspost(
            sr,
            title,
            idn,
            reply_notifications=reply_notifications,
            spoiler=spoiler,
            nsfw=nsfw,
            oc=oc,
            collection_uuid=collection_uuid,
            flair_uuid=flair_uuid,
            flair_text=flair_text,
            event_start=event_start,
            event_end=event_end,
            event_tz=event_tz,
        )

    def edit_text_post_body(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> TextPost:
        """Edit the body text of a text post.

        .. .PARAMETERS

        :param `int` idn:
        :param body:
            Either markdown or richtext.
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]

        .. .RETURNS

        :rtype: :class:`~.models.submission_SYNC.TextPost`

        .. .RAISES

        :raises:
            Same as comment :meth:`~.siteprocs.comment.SYNC.CommentProcedures.edit_body`
            but for submissions.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't3_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = self._client.request('POST', '/api/editusertext', files=dict(g()))
        return load_text_post(result, self._client)

    def delete(self, idn: int) -> None:
        """Delete a submission.

        If the target doesn't exist or isn't valid, nothing happens.

        When a submission is deleted it's text content (if a text post)
        will be set to "`[deleted]`" and the submission will be unlisted
        from its subreddit. Users can still otherwise view and reply to
        deleted to submissions if they have a direct link to it.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/del', data=data)

    def lock(self, idn: int) -> None:
        """Lock a submission.

        Nothing happens if the target is already locked.

        .. hint::
           Locking prevents a submission/comment from receiving new comments.
           A locked submission is unable to receive any new comments.
           Locking a comment only stops direct comments, but
           existing child comments can still receive replies.

        .. .PARAMETERS

        :param `int` idn:

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
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/lock', data=data)

    def unlock(self, idn: int) -> None:
        """Unlock a submission.

        Behaves similarly to :meth:`.lock`.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises:
            Similar to :meth:`.lock`.
        """
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/unlock', data=data)

    def vote(self, idn: int, direction: int) -> None:
        """Cast a vote on a submission.

        .. .PARAMETERS

        :param `int` idn:
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
        data = {
            'id': 't3_' + to_base36(idn),
            'dir': str(direction),
        }
        self._client.request('POST', '/api/vote', data=data)

    def save(self, idn: int, category: Optional[str] = None) -> None:
        """Save a submission.

        .. .PARAMETERS

        :param `int` idn:
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
        data = {
            'id': 't3_' + to_base36(idn),
        }
        if category is not None:
            data['category'] = category
        self._client.request('POST', '/api/save', data=data)

    def unsave(self, idn: int) -> None:
        """Save a submission.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/unsave', data=data)

    def hide(self, idn: int) -> None:
        """Hide a submission.

        .. .PARAMETERS

        :param `int` idn:

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
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/hide', data=data)

    def unhide(self, idn: int) -> None:
        """Unhide a submission.

        See :meth:`.hide`.
        """
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/unhide', data=data)

    def bulk_hide(self, ids: Iterable[int]) -> CallChunkCallingIterator[None]:
        """Bulk hide submissions.

        If *any* of the list of submission IDs don't exist then the endpoint will
        return a HTTP 400 status error and none of the submissions will be hidden.
        This can be annoying since if the list is long it can be hard to tell which
        ID is the culprit.

        .. .PARAMETERS

        :param `Iterable[int]` ids:

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_calling_iterator.CallChunkCallingIterator`\\[`None`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                If any of the IDs were not found.
        """
        def mass_hide(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            self._client.request('POST', '/api/hide', data={'id': ids_str})

        return CallChunkCallingIterator(CallChunk(mass_hide, chunk) for chunk in chunked(ids, 300))

    def bulk_unhide(self, ids: Iterable[int]) -> CallChunkCallingIterator[None]:
        """Bulk hide submissions.

        See :meth:`.bulk_hide`.
        """
        def mass_unhide(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            full_id36s = map('t3_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            self._client.request('POST', '/api/unhide', data={'id': ids_str})

        return CallChunkCallingIterator(CallChunk(mass_unhide, chunk) for chunk in chunked(ids, 300))

    def mark_nsfw(self, idn: int) -> None:
        """Mark a submission as NSFW.

        .. .PARAMETERS

        :param `int` idn:

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
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/marknsfw', data=data)

    def unmark_nsfw(self, idn: int) -> None:
        """Unmark a submission as NSFW.

        See :meth:`.mark_nsfw`.
        """
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/unmarknsfw', data=data)

    def mark_spoiler(self, idn: int) -> None:
        """Mark a submission as spoiler.

        .. .PARAMETERS

        :param `int` idn:

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
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/spoiler', data=data)

    def unmark_spoiler(self, idn: int) -> None:
        """Unmark a submission as spoiler.

        See :meth:`.mark_spoiler`.
        """
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/unspoiler', data=data)

    def distinguish(self, idn: int) -> Submission:
        """Distinguish a submission.

        .. hint::

           Distinguishing decoratates the author's name by
           giving it a different color and putting a sigil beside it.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :returns: The target submission.
        :rtype: :class:`~.models.submission_SYNC.Submission`

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
        data = {
            'id': 't3_' + to_base36(idn),
            'how': 'yes',
        }
        root = self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    def undistinguish(self, idn: int) -> Submission:
        """Undistinguish a submission.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :returns: The target submission.
        :rtype: :class:`~.models.submission_SYNC.Submission`

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
        data = {
            'id': 't3_' + to_base36(idn),
            'how': 'no',
        }
        root = self._client.request('POST', '/api/distinguish', data=data)
        return load_submission(root['json']['data']['things'][0]['data'], self._client)

    def sticky(self, idn: int, slot: Optional[int] = None) -> None:
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

        :param `int` idn:
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
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '1',
        }
        if slot is not None:
            data['num'] = str(slot)
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def unsticky(self, idn: int) -> None:
        """Unsticky a submission.

        See :meth:`.sticky`.

        Unstickying a post that isn't stickied does nothing.
        """
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '0',
        }
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def pin_to_profile(self, idn: int, slot: Optional[int] = None) -> None:
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

        :param `int` idn:
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
        data = {
            'id': 't3_' + to_base36(idn),
            'to_profile': '1',
            'state': '1',
        }
        if slot is not None:
            data['num'] = str(slot)
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def unpin_from_profile(self, idn: int) -> None:
        """Unpin a submission from your user profile.

        See :meth:`.pin_to_profile`.

        Unpinning a post that isn't pinned does nothing.
        """
        data = {
            'id': 't3_' + to_base36(idn),
            'to_profile': '1',
            'state': '0',
        }
        self._client.request('POST', '/api/set_subreddit_sticky', data=data)

    def set_contest_mode(self, idn: int, state: bool) -> None:
        """Set or unset 'contest mode' for a submission's comments.

        .. hint::

            In contest mode, vote counts are hidden and comments are displayed
            in a random order.

        .. .PARAMETERS

        :param `int` idn:
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
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '01'[state],
        }
        self._client.request('POST', '/api/set_contest_mode', data=data)

    def set_suggested_sort(self, idn: int, sort: str) -> None:
        """Set or unset the suggested sort for a submission's comments.

        .. hint::

           When set, users will see comments in the suggested sort order by default.
           They can still manually change back to their preferred sort if they choose.

        .. .PARAMETERS

        :param `int` idn:
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
        data = {
            'id': 't3_' + to_base36(idn),
            'sort': sort,
        }
        self._client.request('POST', '/api/set_suggested_sort', data=data)

    def enable_reply_notifications(self, idn: int) -> None:
        """Enable inbox reply notifications for a submission.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '1'
        }
        self._client.request('POST', '/api/sendreplies', data=data)

    def disable_reply_notifications(self, idn: int) -> None:
        """Disable inbox reply notifications for a submission.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        data = {
            'id': 't3_' + to_base36(idn),
            'state': '0'
        }
        self._client.request('POST', '/api/sendreplies', data=data)

    def set_event_time(self, idn: int,
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

        :param `int` idn:
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
            yield ('id', 't3_' + to_base36(idn))
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        self._client.request('POST', '/api/event_post_time', data=dict(g()))

    def follow_event(self, idn: int) -> None:
        """Follow a post event.

        .. hint::
           Followers receive a push notification when the event starts.

        .. .PARAMETERS

        :param `int` idn:

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
        data = {
            'fullname': 't3_' + to_base36(idn),
            'follow': '1',
        }
        self._client.request('POST', '/api/follow_post', data=data)

    def unfollow_event(self, idn: int) -> None:
        """Unfollow a post event.

        See :meth:`.follow_event`.
        """
        data = {
            'fullname': 't3_' + to_base36(idn),
            'follow': '0',
        }
        self._client.request('POST', '/api/follow_post', data=data)

    def approve(self, idn: int) -> None:
        """Approve a submission.

        .. .PARAMETERS

        :param `int` idn:

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
        data = {'id': 't3_' + to_base36(idn)}
        self._client.request('POST', '/api/approve', data=data)

    def remove(self, idn: int) -> None:
        """Remove a submission.

        This is a moderator action.

        .. .PARAMETERS

        :param `int` idn:

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
        data = {
            'id': 't3_' + to_base36(idn),
            'spam': '0',
        }
        self._client.request('POST', '/api/remove', data=data)

    def remove_spam(self, idn: int) -> None:
        """Remove as spam.

        See :meth:`.remove`.
        """
        data = {
            'id': 't3_' + to_base36(idn),
            'spam': '1',
        }
        self._client.request('POST', '/api/remove', data=data)

    def ignore_reports(self, idn: int) -> None:
        """Ignore reports on a submission.

        .. hint::
           If you ignore reports, you won't receive notifications and the
           ignored thing will be absent from moderation listings.

        Nothing happens if the target is already ignored.

        .. .PARAMETERS

        :param `int` idn:
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
        self._client.request('POST', '/api/ignore_reports', data={'id': 't3_' + to_base36(idn)})

    def unignore_reports(self, idn: int) -> None:
        """Unignore reports on a submission.

        Nothing happens if the target is already unignored.

        .. .PARAMETERS

        :param `int` idn:
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
        self._client.request('POST', '/api/unignore_reports', data={'id': 't3_' + to_base36(idn)})

    def snooze_reports(self, idn: int, reason: str) -> None:
        """Ignore a custom report reason in a subreddit for 7 days.

        .. .PARAMETERS

        :param `int` idn:
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
        data = {'id': 't3_' + to_base36(idn), 'reason': reason}
        self._client.request('POST', '/api/snooze_reports', data=data)

    def unsnooze_reports(self, idn: int, reason: str) -> None:
        """Unsnooze a custom report.

        See :meth:`.snooze_reports`.
        """
        data = {'id': 't3_' + to_base36(idn), 'reason': reason}
        self._client.request('POST', '/api/unsnooze_reports', data=data)

    def apply_removal_reason(self,
            idn: int,
            reason_id: Optional[str] = None,
            note: Optional[str] = None) -> None:
        """Set a removal reason on a removed submission.

        If the target is not a removed submission, nothing happens.

        .. .PARAMETERS

        :param `int` idn:
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
        target = 't3_' + to_base36(idn)
        json_data = {'item_ids': [target], 'reason_id': reason_id, 'mod_note': note}
        self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    def send_removal_comment(self,
            idn: int,
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

        :param `int` idn:
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
        :rtype: :class:`~.models.comment_SYNC.Comment`

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
        target = 't3_' + to_base36(idn)
        json_data = {
            'type': 'public' + ('' if exposed else '_as_subreddit'),
            'item_id': [target],
            'title': title,
            'message': message,
            'lock_comment': '01'[locked],
        }
        root = self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)
        return load_comment(root, self._client)

    def send_removal_message(self,
            idn: int,
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        """Send a removal message.

        Behaves similarly to :meth:`.send_removal_comment`.

        .. .PARAMETERS

        :param `int` idn:
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
        target = 't3_' + to_base36(idn)
        json_data = {
            'type': 'private' + ('_exposed' if exposed else ''),
            'item_id': [target],
            'title': title,
            'message': message,
        }
        self._client.request('POST', '/api/v1/modactions/removal_link_message', json=json_data)

    def search(self, sr: str, query: str, amount: Optional[int] = None, *,
        sort: str = 'relevance', time: str = 'all',
    ) -> ImpartedPaginatorChainingIterator[SubmissionSearchPaginator, Submission]:
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

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.submission_sync1.SubmissionSearchPaginator`, :class:`~.models.submission_SYNC.Submission`]
        """
        url = '/search'
        if sr:
            url = f'/r/{sr}/search'
        p = SubmissionSearchPaginator(
                self._client, url,
                params={'q': query, 'restrict_sr': '1'},
                    sort=sort, time=time)
        return ImpartedPaginatorChainingIterator(p, amount)

    def duplicates(self, target: int, amount: Optional[int] = None, *,
        sort: str = 'num_comments',
    ) -> ImpartedPaginatorChainingIterator[SubmissionDuplicatesPaginator, Submission]:
        """Get crossposts for a submission.

        .. .PARAMETERS

        :param `int` target:
            Submission ID.
        :param `Optional[int]` amount:
            The number of items to retrieve.
        :param `str` sort:
            Either `num_comments` or `new`.

            Default: `num_comments`.

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.submission_sync1.SubmissionDuplicatesPaginator`, :class:`~.models.submission_SYNC.Submission`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                Fetching some submissions resulted in a 403.
            + `404`:
                The target submission could not be found.
        """
        subm_id = to_base36(target)
        p = SubmissionDuplicatesPaginator(self._client, f'/duplicates/{subm_id}', sort=sort)
        return ImpartedPaginatorChainingIterator(p, amount)
