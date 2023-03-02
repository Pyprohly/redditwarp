
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, Union, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_ASYNC import Comment
    from ...types import JSON_ro

import json

from ...model_loaders.comment_ASYNC import load_comment
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from .fetch_ASYNC import Fetch
from .get_ASYNC import Get

class CommentProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch: Fetch = Fetch(self, client)
        ("""
            Fetch a comment.

            .. .PARAMETERS

            :param `int` idn:
                Comment ID.

            .. .RETURNS

            :rtype: :class:`~.models.comment_ASYNC.Comment`

            .. .RAISES

            :raises redditwarp.exceptions.NoResultException:
                The target was not found.
            """)
        self.get: Get = Get(client)
        ("""
            Get a comment.

            .. .PARAMETERS

            :param `int` idn:
                Comment ID.

            .. .RETURNS

            :rtype: `Optional`\\[:class:`~.models.comment_ASYNC.Comment`]
            """)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingAsyncIterator[Comment]:
        """Bulk fetch comments.

        Any ID not found will be ignored.

        .. .PARAMETERS

        :param `Iterable[int]` ids:
            Comment IDs.

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_chaining_async_iterator.CallChunkChainingAsyncIterator`\\[:class:`~.models.comment_ASYNC.Comment`]
        """
        async def mass_fetch(ids: Sequence[int]) -> Sequence[Comment]:
            id36s = map(to_base36, ids)
            full_id36s = map('t1_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = await self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_comment(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))

    async def reply(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> Comment:
        """Reply to a comment.

        .. .PARAMETERS

        :param `int` idn:
        :param body:
            Either markdown or richtext.
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]

        .. .RETURNS

        :rtype: :class:`~.models.comment_ASYNC.Comment`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `RATELIMIT`:
                Content creation cooldown.
            + `NO_TEXT`:
                The specified `body` was empty.
            + `TOO_OLD`:
                The subreddit has archiving enabled and the target comment
                is archived (older than 6 months).
            + `THREAD_LOCKED`:
                The target comment submission is locked and you are not a
                moderator of the subreddit.
            + `DELETED_COMMENT`:
                The target comment was deleted.
            + `SOMETHING_IS_BROKEN`:
                The author of the target comment has blocked you.
            + `USER_BLOCKED`:
                The author of the target comment is a user you have blocked.
            + `SUBREDDIT_OUTBOUND_LINKING_DISALLOWED`:
                Some subreddits prevent you from linking to other subreddits. E.g.,
                writing 'r/funny' in 'r/formuladank'. It is not known what setting
                controls this.
            + `SUBREDDIT_LINKING_DISALLOWED`:
                Some subreddits cannot be linked to at all. E.g., 'r/chonglangTV'.
                It is unknown why.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The target comment does not exist.
            + `500`:
                The target comment is from a quarantined subreddit that the
                current user has not opted in to.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't1_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/comment', files=dict(g()))
        return load_comment(result, self._client)

    async def edit_body(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> Comment:
        """Edit the body text of a comment.

        The target entity (with the new body text) is returned.

        .. .PARAMETERS

        :param `int` idn:
        :param body:
            Either markdown or richtext.
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]

        .. .RETURNS

        :rtype: :class:`~.models.comment_ASYNC.Comment`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_THING_ID`:
                The target comment does not exist.
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't1_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/editusertext', files=dict(g()))
        return load_comment(result, self._client)

    async def delete(self, idn: int) -> None:
        """Delete a comment.

        If the target doesn't exist or isn't valid, nothing happens.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/del', data=data)

    async def lock(self, idn: int) -> None:
        """Lock a comment.

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
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/lock', data=data)

    async def unlock(self, idn: int) -> None:
        """Unlock a comment.

        Behaves similarly to :meth:`.lock`.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises:
            Similar to :meth:`.lock`.
        """
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/unlock', data=data)

    async def vote(self, idn: int, direction: int) -> None:
        """Cast a vote on a comment.

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
            'id': 't1_' + to_base36(idn),
            'dir': str(direction),
        }
        await self._client.request('POST', '/api/vote', data=data)

    async def save(self, idn: int, category: Optional[str] = None) -> None:
        """Save a comment.

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
            'id': 't1_' + to_base36(idn),
        }
        if category is not None:
            data['category'] = category
        await self._client.request('POST', '/api/save', data=data)

    async def unsave(self, idn: int) -> None:
        """Save a comment.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/unsave', data=data)

    async def distinguish(self, idn: int) -> Comment:
        """Distinguish a comment.

        .. hint::
           Distinguishing decoratates the author's name by
           giving it a different color and putting a sigil beside it.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :returns: The target comment.
        :rtype: :class:`~.models.comment_ASYNC.Comment`

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
            'id': 't1_' + to_base36(idn),
            'how': 'yes',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def distinguish_and_sticky(self, idn: int) -> Comment:
        """Distinguish and sticky a comment.

        Only one comment may be stickied at a time. Attempting to sticky a comment
        when there is already a stickied comment will override that stickied comment.
        Only top-level comments may be stickied.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :returns: The target comment.
        :rtype: :class:`~.models.comment_ASYNC.Comment`

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
            'id': 't1_' + to_base36(idn),
            'how': 'yes',
            'sticky': '1',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def undistinguish(self, idn: int) -> Comment:
        """Undistinguish a comment.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :returns: The target comment.
        :rtype: :class:`~.models.comment_ASYNC.Comment`

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
            'id': 't1_' + to_base36(idn),
            'how': 'no',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def enable_reply_notifications(self, idn: int) -> None:
        """Enable inbox reply notifications for a comment.

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
            'id': 't1_' + to_base36(idn),
            'state': '1'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def disable_reply_notifications(self, idn: int) -> None:
        """Disable inbox reply notifications for a comment.

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
            'id': 't1_' + to_base36(idn),
            'state': '0'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def approve(self, idn: int) -> None:
        """Approve a comment.

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
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/approve', data=data)

    async def remove(self, idn: int) -> None:
        """Remove a comment.

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
            'id': 't1_' + to_base36(idn),
            'spam': '0',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def remove_spam(self, idn: int) -> None:
        """Remove as spam.

        See :meth:`.remove`.
        """
        data = {
            'id': 't1_' + to_base36(idn),
            'spam': '1',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def ignore_reports(self, idn: int) -> None:
        """Ignore reports on a comment.

        .. hint::
           If you ignore reports, you won't receive notifications and the
           ignored thing will be absent from moderation listings.

        Nothing happens if the target is already ignored.

        .. .PARAMETERS

        :param `int` idn:
            Comment ID.

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
        await self._client.request('POST', '/api/ignore_reports', data={'id': 't1_' + to_base36(idn)})

    async def unignore_reports(self, idn: int) -> None:
        """Unignore reports on a comment.

        Nothing happens if the target is already unignored.

        .. .PARAMETERS

        :param `int` idn:
            Comment ID.

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
        await self._client.request('POST', '/api/unignore_reports', data={'id': 't1_' + to_base36(idn)})

    async def snooze_reports(self, idn: int, reason: str) -> None:
        """Ignore a custom report reason in a subreddit for 7 days.

        .. .PARAMETERS

        :param `int` idn:
            Comment ID.
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
        data = {'id': 't1_' + to_base36(idn), 'reason': reason}
        await self._client.request('POST', '/api/snooze_reports', data=data)

    async def unsnooze_reports(self, idn: int, reason: str) -> None:
        """Unsnooze a custom report.

        See :meth:`.snooze_reports`.
        """
        data = {'id': 't1_' + to_base36(idn), 'reason': reason}
        await self._client.request('POST', '/api/unsnooze_reports', data=data)

    async def apply_removal_reason(self,
            idn: int,
            reason_id: Optional[str] = None,
            note: Optional[str] = None) -> None:
        """Set a removal reason on a removed comment.

        If the target is not a removed comment, nothing happens.

        .. .PARAMETERS

        :param `int` idn:
            Comment ID.
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
        target = 't1_' + to_base36(idn)
        json_data = {'item_ids': [target], 'reason_id': reason_id, 'mod_note': note}
        await self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    async def send_removal_comment(self,
            idn: int,
            title: str,
            message: str,
            *,
            exposed: bool = False,
            locked: bool = False) -> Comment:
        """Send a removal comment.

        Sends a removal reason comment to a user for a removed comment of theirs.

        This action can be performed multiple times.
        (The UI does not normally let you do this.)

        Unlike :meth:`.apply_removal_reason`, the target you specify must be a
        removed item otherwise an `INVALID_ID` API error is produced.

        .. .PARAMETERS

        :param `int` idn:
            ID of a removed comment.
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
        target = 't1_' + to_base36(idn)
        json_data = {
            'type': 'public' + ('' if exposed else '_as_subreddit'),
            'item_id': [target],
            'title': title,
            'message': message,
            'lock_comment': '01'[locked],
        }
        root = await self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
        return load_comment(root, self._client)

    async def send_removal_message(self,
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
        target = 't1_' + to_base36(idn)
        json_data = {
            'type': 'private' + ('_exposed' if exposed else ''),
            'item_id': [target],
            'title': title,
            'message': message,
        }
        await self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
