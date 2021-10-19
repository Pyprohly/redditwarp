
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, Sequence, Iterable, Tuple
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..cursor_paginator import CursorPaginator
from ..exceptions import MissingCursorException
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
        self.limit = limit
        self.client = client
        self.uri = uri
        self.mailbox = mailbox
        self.subreddit_names = subreddit_names
        self.sort = sort

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        if self.limit is not None:
            yield ('limit', str(self.limit))

        if self.after:
            yield ('after', self.after)
        elif not self.has_after:
            raise MissingCursorException('after')

        if self.mailbox:
            yield ('state', self.mailbox)
        if self.subreddit_names:
            yield ('entity', ','.join(self.subreddit_names))
        if self.sort:
            yield ('sort', self.sort)

    def _next_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        data = self.client.request('GET', self.uri, params=params)
        entries = data['conversationIds']

        if entries:
            self.after = entries[-1]

        self.has_after = bool(entries)
        return data

    def next_result(self) -> Sequence[Tuple[Conversation, Message]]:
        data = self._next_data()
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
