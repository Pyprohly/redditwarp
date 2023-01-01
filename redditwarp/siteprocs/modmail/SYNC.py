
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.modmail import ModeratedSubreddit

from ...model_loaders.modmail import load_moderated_subreddit
from .conversation_SYNC import ConversationProcedures
from .pull_SYNC import Pull

class ModmailProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.conversation: ConversationProcedures = ConversationProcedures(client)
        self.pull: Pull = Pull(client)

    def get_unread_counts(self) -> Mapping[str, int]:
        return self._client.request('GET', '/api/mod/conversations/unread/count')

    def get_moderated_subreddits(self) -> Sequence[ModeratedSubreddit]:
        root = self._client.request('GET', '/api/mod/conversations/subreddits')
        return [load_moderated_subreddit(d) for d in root['subreddits'].values()]
