
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.modmail import ModeratedSubreddit

from ...model_loaders.modmail import load_moderated_subreddit
from .conversation_ASYNC import ConversationProcedures
from .pull_ASYNC import Pull

class ModmailProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.conversation: ConversationProcedures = ConversationProcedures(client)
        self.pull: Pull = Pull(client)

    async def get_unread_counts(self) -> Mapping[str, int]:
        return await self._client.request('GET', '/api/mod/conversations/unread/count')

    async def get_moderated_subreddits(self) -> Sequence[ModeratedSubreddit]:
        root = await self._client.request('GET', '/api/mod/conversations/subreddits')
        return [load_moderated_subreddit(d) for d in root['subreddits'].values()]
