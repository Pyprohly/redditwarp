
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.message_ASYNC import MailboxMessage
    from ..stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ...models.message_ASYNC import ComposedMessage, CommentMessage
from ..stream_ASYNC import Stream


def get_inbox_message_stream_paginator(client: Client) -> CursorAsyncPaginator[MailboxMessage]:
    return client.p.message.pulls.inbox().get_paginator()

def make_inbox_message_stream(paginator: CursorAsyncPaginator[MailboxMessage], seen: Iterable[MailboxMessage] = ()) -> IStandardStreamEventSubject[MailboxMessage]:
    def extractor(message: MailboxMessage) -> tuple[int, int]:
        if isinstance(message, ComposedMessage):
            return (0, message.id)
        elif isinstance(message, CommentMessage):
            return (1, message.comment.id)
        raise Exception

    return Stream(paginator, extractor, seen)

def create_inbox_message_stream(client: Client) -> IStandardStreamEventSubject[MailboxMessage]:
    return make_inbox_message_stream(get_inbox_message_stream_paginator(client))


def get_mentions_message_stream_paginator(client: Client) -> CursorAsyncPaginator[CommentMessage]:
    return client.p.message.pulls.mentions().get_paginator()

def make_mentions_message_stream(paginator: CursorAsyncPaginator[CommentMessage], seen: Iterable[CommentMessage] = ()) -> IStandardStreamEventSubject[CommentMessage]:
    return Stream(paginator, lambda x: x.comment.id, seen)

def create_mentions_message_stream(client: Client) -> IStandardStreamEventSubject[CommentMessage]:
    return make_mentions_message_stream(get_mentions_message_stream_paginator(client))
