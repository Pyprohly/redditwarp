
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.moderation_note import ModerationUserNote

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.moderation.note_pulls_async1 import ModerationNoteAsyncPaginator
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...model_loaders.moderation_note import load_moderation_user_note
from ... import http

class Note:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def create_user_note(self, subreddit: str, user: str, note: str, *,
            label: str = '',
            anchor_submission_id: Optional[int] = None,
            anchor_comment_id: Optional[int] = None) -> ModerationUserNote:
        mxp = (anchor_submission_id, anchor_comment_id)
        if len(mxp) - mxp.count(None) > 1:
            raise TypeError("mutually exclusive parameters: `anchor_submission_id`, `anchor_comment_id`.")

        params = {'subreddit': subreddit, 'user': user, 'label': label}
        root = await self._client.request('POST', '/api/mod/notes', params=params)
        return load_moderation_user_note(root['created'])

    def pulls(self,
        subreddit: str,
        user: str,
        amount: Optional[int] = None,
        *,
        type: Optional[str] = None,
    ) -> ImpartedPaginatorChainingAsyncIterator[ModerationNoteAsyncPaginator, ModerationUserNote]:
        p = ModerationNoteAsyncPaginator(
            client=self._client,
            url='/api/mod/notes',
            subreddit=subreddit,
            user=user,
            type=type,
        )
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def delete(self, note_uuid: str, subreddit: str, user: str) -> None:
        params = {'note_id': 'ModNote_' + note_uuid, 'subreddit': subreddit, 'user': user}
        await self._client.request('DELETE', '/api/mod/notes', params=params)

    async def get_latest_user_note(self, subreddit: str, user: str) -> Optional[ModerationUserNote]:
        params = {'subreddits': subreddit, 'users': user}
        try:
            root = await self._client.request('GET', '/api/mod/notes/recent', params=params)
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 400:
                return None
            raise
        return load_moderation_user_note(root['mod_notes'][0])

    def bulk_get_latest_user_note(self, pairs: Iterable[tuple[str, str]]) -> CallChunkChainingAsyncIterator[Optional[ModerationUserNote]]:
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
