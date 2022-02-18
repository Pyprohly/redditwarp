
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Sequence, Iterable, Tuple
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..paginator import CursorPaginator
from ...models.load.modmail_SYNC import load_conversation, load_message
from ...models.modmail_SYNC import Conversation, Message

class ModmailConversationsPaginator(CursorPaginator[Tuple[Conversation, Message]]):
    def __init__(self,
        client: Client,
        uri: str,
        mailbox: str,
        subreddit_names: Sequence[str],
        sort: str,
        *,
        limit: Optional[int] = 100,
    ):
        super().__init__()
        self.limit: Optional[int] = limit
        self.client: Client = client
        self.uri: str = uri
        self.mailbox: str = mailbox
        self.subreddit_names: Sequence[str] = subreddit_names
        self.sort: str = sort
        self._after: str = ''
        self._has_after: bool = True

    def get_cursor(self) -> str:
        return self._after

    def set_cursor(self, value: str) -> None:
        self._after = value

    def more_available(self) -> bool:
        return self._has_after

    def set_more_available_flag(self, value: bool) -> None:
        self._has_after = value

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        if self.limit is not None:
            yield ('limit', str(self.limit))

        if self._after:
            yield ('after', self._after)

        if self.mailbox:
            yield ('state', self.mailbox)
        if self.subreddit_names:
            yield ('entity', ','.join(self.subreddit_names))
        if self.sort:
            yield ('sort', self.sort)

    def _fetch_data(self) -> Any:
        params = dict(self._generate_params())
        data = self.client.request('GET', self.uri, params=params)
        entries = data['conversationIds']

        if entries:
            self._after = entries[-1]
        self._has_after = bool(entries)

        return data

    def fetch(self) -> Sequence[Tuple[Conversation, Message]]:
        data = self._fetch_data()
        conversations_mapping = data['conversations']
        messages_mapping = data['messages']
        results = []
        for convo_id36 in data['conversationIds']:
            conversation_data = conversations_mapping[convo_id36]
            message_id36 = conversation_data['objIds'][0]['id']
            message_data = messages_mapping[message_id36]
            results.append(
                (
                    load_conversation(conversation_data, self.client),
                    load_message(message_data, self.client),
                )
            )
        return results
