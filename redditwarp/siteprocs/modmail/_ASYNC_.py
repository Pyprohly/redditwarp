
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.modmail import ModmailModeratedSubreddit

from ...models.load.modmail import load_modmail_moderated_subreddit
from .conversation_ASYNC import ConversationProcedures

class ModmailProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.conversation: ConversationProcedures = ConversationProcedures(client)

    async def get_unread_counts(self) -> Mapping[str, int]:
        return await self._client.request('GET', '/api/mod/conversations/unread/count')

    async def get_moderating_subreddits(self) -> Sequence[ModmailModeratedSubreddit]:
        root = await self._client.request('GET', '/api/mod/conversations/subreddits')
        return [load_modmail_moderated_subreddit(d) for d in root['subreddits'].values()]
