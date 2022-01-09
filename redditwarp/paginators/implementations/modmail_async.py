
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, Sequence, Iterable, Tuple
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ..cursor_async_paginator import CursorAsyncPaginator
from ..exceptions import MissingCursorException
from ...models.load.modmail_ASYNC import load_conversation, load_message
from ...models.modmail_ASYNC import Conversation, Message

class ModmailConversationsAsyncPaginator(CursorAsyncPaginator[Tuple[Conversation, Message]]):
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

    async def _fetch_next_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        data = await self.client.request('GET', self.uri, params=params)
        entries = data['conversationIds']

        if entries:
            self.after: str = entries[-1]

        self.has_after: bool = bool(entries)
        return data

    async def fetch_next(self) -> Sequence[Tuple[Conversation, Message]]:
        data = await self._fetch_next_data()
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
