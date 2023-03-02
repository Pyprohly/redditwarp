
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.moderation_note import (
        ModerationNote,
        ModerationUserNote,
    )

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.moderation.note_pulls_async1 import (
    ModerationNoteAsyncPaginator,
    ModerationUserNoteAsyncPaginator,
)
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...model_loaders.moderation_note import load_moderation_user_note
from ... import http

class Note:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def create_user_note(self, sr: str, user: str, content: str, *,
            label: str = '',
            anchor_submission_id: Optional[int] = None,
            anchor_comment_id: Optional[int] = None) -> ModerationUserNote:
        """Create a user note.

        .. .PARAMETERS

        :param `str` sr:
            Subreddit name.
        :param `str` user:
            User name.
        :param `str` content:
            Content of the note. Max 250 characters.
        :param `str` label:
            Either: `BOT_BAN`, `PERMA_BAN`, `BAN`, `ABUSE_WARNING`, `SPAM_WARNING`,
            `SPAM_WATCH`, `SOLID_CONTRIBUTOR`, `HELPFUL_USER`.
        :param `Optional[str]` anchor_submission_id:
            A submission ID to link the note to.

            Mutually exclusive with `anchor_comment_id`.
        :param `Optional[str]` anchor_comment_id:
            A comment ID to link the note to.

            Mutually exclusive with `anchor_submission_id`.

        .. .RETURNS

        :rtype: :class:`~.models.moderation_note.ModerationUserNote`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_DOESNT_EXIST`:
                The specified user does not exist.
            + `BAD_SR_NAME`:
                The specified subreddit does not exist.
            + `NO_TEXT`:
                The content of the note was empty.
            + `TOO_LONG`:
                The content of the note was too long, over 250 characters.
            + `INVALID_OPTION`:
                The label specified was invalid.
            + `NO_THING_ID`:
                The linked submission or comment does not exist.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You are not a moderator of the target subreddit.
        """
        mxp = (anchor_submission_id, anchor_comment_id)
        if len(mxp) - mxp.count(None) > 1:
            raise TypeError("mutually exclusive parameters: `anchor_submission_id`, `anchor_comment_id`.")

        params = {'subreddit': sr, 'user': user, 'note': content, 'label': label}
        root = await self._client.request('POST', '/api/mod/notes', params=params)
        return load_moderation_user_note(root['created'])

    async def delete(self, sr: str, user: str, uuid: str) -> None:
        """Delete a moderation note.

        This procedure can be used to delete either a user or action type note.

        In addition to the note ID, the endpoint must be given the subreddit and
        user name in which the note belongs. If either information is incorrect,
        the endpoint will raise a 500 HTTP error.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `str` uuid:
            UUID of a note.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `BAD_SR_NAME`:
                The `sr` parameter was empty.
            + `SUBREDDIT_NOEXIST`:
                The target subreddit does not exist.
            + `USER_DOESNT_EXIST`:
               - The specified user does not exist.
               - The `user` parameter was empty.
            + `PARAMETER_REQUIRED`:
                The `uuid` parameter was empty.
            + `INVALID_ID`:
                The specified user does not exist.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `500`:
               - The subreddit or user specified is incorrect for the given note ID.
               - The given note ID was invalid.
        """
        params = {'subreddit': sr, 'user': user, 'note_id': 'ModNote_' + uuid}
        await self._client.request('DELETE', '/api/mod/notes', params=params)

    def pull_notes(self,
        sr: str,
        user: str,
        amount: Optional[int] = None,
        *,
        label: Optional[str] = None,
    ) -> ImpartedPaginatorChainingAsyncIterator[ModerationNoteAsyncPaginator, ModerationNote]:
        """Get moderation notes of a user in a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:
        :param `Optional[int]` amount:
        :param `Optional[str]` label:
            Filter by note type.

            Either: `ALL`, `NOTE`, `APPROVAL`, `REMOVAL`, `BAN`, `MUTE`,
            `INVITE`, `SPAM`, `CONTENT_CHANGE`.

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_async_iterator.ImpartedPaginatorChainingAsyncIterator`\\[:class:`~.pagination.paginators.moderation.note_pulls_async1.ModerationNoteAsyncPaginator`, :class:`~.models.moderation_note.ModerationNote`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `BAD_SR_NAME`:
                The `sr` parameter was empty.
            + `SUBREDDIT_NOEXIST`:
                The target subreddit does not exist.
            + `USER_DOESNT_EXIST`:
               - The specified user does not exist.
               - The `user` parameter was empty.
            + `INVALID_ID`:
                An invalid value was specified for the `label` parameter.
                Values are case-sensitive.
        """
        p = ModerationNoteAsyncPaginator(
            client=self._client,
            url='/api/mod/notes',
            subreddit=sr,
            user=user,
            type=label,
        )
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def pull_user_notes(self,
        sr: str,
        user: str,
        amount: Optional[int] = None,
    ) -> ImpartedPaginatorChainingAsyncIterator[ModerationUserNoteAsyncPaginator, ModerationUserNote]:
        """
        Behaves similarly to :meth:`.pull_notes`.
        """
        p = ModerationUserNoteAsyncPaginator(
            client=self._client,
            url='/api/mod/notes',
            subreddit=sr,
            user=user,
            type='NOTE',
        )
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def get_latest_user_note(self, sr: str, user: str) -> Optional[ModerationUserNote]:
        """Get the most recently written user note for some user.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` user:

        .. .RETURNS

        :rtype: `Optional`\\[:class:`~.models.moderation_note.ModerationUserNote`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `PARAMETER_REQUIRED`:
               - The `sr` parameter was empty.
               - The `user` parameter was empty.
        """
        params = {'subreddits': sr, 'users': user}
        try:
            root = await self._client.request('GET', '/api/mod/notes/recent', params=params)
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 400:
                return None
            raise
        note_obj = root['mod_notes'][0]
        if note_obj is None:
            return None
        return load_moderation_user_note(note_obj)

    def bulk_get_latest_user_note(self, pairs: Iterable[tuple[str, str]]) -> CallChunkChainingAsyncIterator[Optional[ModerationUserNote]]:
        """Bulk fetch the most recently written user notes for users.

        The response contains a list of mod notes in the order that subreddits and users were given.
        If no note exists for a given pair, `None` will take its place in the list.

        .. .PARAMETERS

        :param `Iterable[tuple[str, str]]` pairs:

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_chaining_async_iterator.CallChunkChainingAsyncIterator`\\[`Optional`\\[:class:`~.models.moderation_note.ModerationUserNote`]]

        .. .RAISES

        :(raises): Same as :meth:`.get_latest_user_note`.
        """
        async def mass_get_latest_user_note(pairs: Sequence[tuple[str, str]]) -> Sequence[Optional[ModerationUserNote]]:
            subreddits, users = tuple(zip(*pairs))
            subreddits_str = ','.join(subreddits)
            users_str = ','.join(users)
            params = {'subreddits': subreddits_str, 'users': users_str}
            try:
                root = await self._client.request('GET', '/api/mod/notes/recent', params=params)
            except http.exceptions.StatusCodeException as e:
                if e.status_code == 400:
                    return [None]
                raise
            return [
                (None if note_obj is None else load_moderation_user_note(note_obj))
                for note_obj in root['mod_notes']
            ]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_get_latest_user_note, chunk) for chunk in chunked(pairs, 500))
