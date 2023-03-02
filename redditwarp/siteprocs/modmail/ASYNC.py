
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.modmail import ModmailSubreddit

from ...model_loaders.modmail import load_modmail_subreddit
from .conversation_ASYNC import ConversationProcedures
from .pull_ASYNC import Pull

class ModmailProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.conversation: ConversationProcedures = ConversationProcedures(client)
        self.pull: Pull = Pull(client)

    async def get_unread_counts(self) -> Mapping[str, int]:
        """Get unread conversations counts by mailbox.

        Returns a dictionary like the following::

           {"archived": 0,
            "appeals": 0,
            "highlighted": 0,
            "notifications": 2,
            "join_requests": 0,
            "filtered": 0,
            "new": 1,
            "inprogress": 0,
            "mod": 0}

        .. .RETURNS

        :rtype: `Mapping`\\[`str`, `int`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        return await self._client.request('GET', '/api/mod/conversations/unread/count')

    async def subreddits(self) -> Sequence[ModmailSubreddit]:
        """Return subreddits the current user is moderating that have modmail enabled.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.modmail.ModmailSubreddit`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `500`:
                There is no user context.
        """
        root = await self._client.request('GET', '/api/mod/conversations/subreddits')
        return [load_modmail_subreddit(d) for d in root['subreddits'].values()]
