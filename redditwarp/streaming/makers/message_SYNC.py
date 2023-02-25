
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import MailboxMessage
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ...models.message_SYNC import ComposedMessage, CommentMessage
from ..stream_SYNC import Stream


def inbox_message_extractor(x: MailboxMessage) -> object:
    if isinstance(x, ComposedMessage):
        return (0, x.id)
    elif isinstance(x, CommentMessage):
        return (1, x.comment.id)
    raise Exception

def get_inbox_message_stream_paginator(client: Client) -> CursorPaginator[MailboxMessage]:
    return client.p.message.pulls.inbox().get_paginator()

def make_inbox_message_stream(paginator: CursorPaginator[MailboxMessage], past: Optional[Iterable[MailboxMessage]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[MailboxMessage]:
    return Stream(paginator, inbox_message_extractor, past=past, seen=seen)

def create_inbox_message_stream(client: Client) -> IStandardStreamEventSubject[MailboxMessage]:
    return make_inbox_message_stream(get_inbox_message_stream_paginator(client))


def mentions_message_extractor(x: CommentMessage) -> object:
    return x.comment.id

def get_mentions_message_stream_paginator(client: Client) -> CursorPaginator[CommentMessage]:
    return client.p.message.pulls.mentions().get_paginator()

def make_mentions_message_stream(paginator: CursorPaginator[CommentMessage], past: Optional[Iterable[CommentMessage]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[CommentMessage]:
    return Stream(paginator, mentions_message_extractor, past=past, seen=seen)

def create_mentions_message_stream(client: Client) -> IStandardStreamEventSubject[CommentMessage]:
    return make_mentions_message_stream(get_mentions_message_stream_paginator(client))
