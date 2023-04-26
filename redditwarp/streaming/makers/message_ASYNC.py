
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.message_ASYNC import MailboxMessage
    from ..impls.stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ...models.message_ASYNC import ComposedMessage, CommentMessage
from ..impls.stream_ASYNC import SimpleImprintExtractorStream


def get_inbox_message_stream_paginator(client: Client) -> CursorAsyncPaginator[MailboxMessage]:
    return client.p.message.pulls.inbox().get_paginator()

def make_inbox_message_stream(paginator: CursorAsyncPaginator[MailboxMessage], past: Optional[Iterable[MailboxMessage]] = None) -> IStandardStreamEventSubject[MailboxMessage]:
    def inbox_message_extractor(x: MailboxMessage) -> object:
        if isinstance(x, ComposedMessage):
            return (0, x.id)
        elif isinstance(x, CommentMessage):
            return (1, x.comment.id)
        raise Exception
    return SimpleImprintExtractorStream(paginator, inbox_message_extractor, past=past)

def create_inbox_message_stream(client: Client) -> IStandardStreamEventSubject[MailboxMessage]:
    return make_inbox_message_stream(get_inbox_message_stream_paginator(client))


def get_mentions_message_stream_paginator(client: Client) -> CursorAsyncPaginator[CommentMessage]:
    return client.p.message.pulls.mentions().get_paginator()

def make_mentions_message_stream(paginator: CursorAsyncPaginator[CommentMessage], past: Optional[Iterable[CommentMessage]] = None) -> IStandardStreamEventSubject[CommentMessage]:
    def mentions_message_extractor(x: CommentMessage) -> object:
        return x.comment.id
    return SimpleImprintExtractorStream(paginator, mentions_message_extractor, past=past)

def create_mentions_message_stream(client: Client) -> IStandardStreamEventSubject[CommentMessage]:
    return make_mentions_message_stream(get_mentions_message_stream_paginator(client))
