
from __future__ import annotations
from typing import TYPE_CHECKING, Union, overload
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import MailboxMessage
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ...models.message_SYNC import ComposedMessage, CommentMessage
from ..stream_SYNC import Stream


def get_inbox_message_stream_paginator(client: Client) -> CursorPaginator[MailboxMessage]:
    return client.p.message.pulls.inbox().get_paginator()

@overload
def make_inbox_message_stream(paginator: CursorPaginator[MailboxMessage], /) -> IStandardStreamEventSubject[MailboxMessage]: ...
@overload
def make_inbox_message_stream(client: Client, /) -> IStandardStreamEventSubject[MailboxMessage]: ...
def make_inbox_message_stream(arg: Union[CursorPaginator[MailboxMessage], Client]) -> IStandardStreamEventSubject[MailboxMessage]:
    paginator: CursorPaginator[MailboxMessage]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.message.pulls.inbox().get_paginator()
    else:
        paginator = arg
    def extractor(message: MailboxMessage) -> tuple[int, int]:
        if isinstance(message, ComposedMessage):
            return (0, message.id)
        elif isinstance(message, CommentMessage):
            return (1, message.comment.id)
        raise Exception
    return Stream(paginator, extractor)


def get_mentions_message_stream_paginator(client: Client) -> CursorPaginator[CommentMessage]:
    return client.p.message.pulls.mentions().get_paginator()

@overload
def make_mentions_message_stream(paginator: CursorPaginator[CommentMessage], /) -> IStandardStreamEventSubject[CommentMessage]: ...
@overload
def make_mentions_message_stream(client: Client, /) -> IStandardStreamEventSubject[CommentMessage]: ...
def make_mentions_message_stream(arg: Union[CursorPaginator[CommentMessage], Client]) -> IStandardStreamEventSubject[CommentMessage]:
    paginator: CursorPaginator[CommentMessage]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.message.pulls.mentions().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: x.comment.id)
