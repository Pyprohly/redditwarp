
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, IO, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.modmail import ModmailModeratedSubreddit

from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_iterator import CallChunkCallingIterator
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk_SYNC import CallChunk
from ...models.load.modmail import load_modmail_moderated_subreddit
from .conversation_SYNC import Conversation

class Modmail:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.conversation: Conversation = Conversation(client)

    def get_unread_counts(self) -> Mapping[str, int]:
        return self._client.request('GET', '/api/mod/conversations/unread/count')

    def get_moderating_subreddits(self) -> Sequence[ModmailModeratedSubreddit]:
        root = self._client.request('GET', '/api/mod/conversations/subreddits')
        return [load_modmail_moderated_subreddit(d) for d in root['subreddits'].values()]
