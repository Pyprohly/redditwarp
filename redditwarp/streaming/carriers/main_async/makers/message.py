
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....client_ASYNC import Client
    from .....models.message_ASYNC import MailboxMessage
    from ..stream import IStandardStreamEventSubject

from .....models.message_ASYNC import ComposedMessage, CommentMessage
from ..stream import Stream


def make_unread_message_stream(client: Client) -> IStandardStreamEventSubject[MailboxMessage]:
    it = client.p.message.pull.unread()
    paginator = it.get_paginator()
    def extractor(message: MailboxMessage) -> tuple[int, int]:
        if isinstance(message, ComposedMessage):
            return (0, message.id)
        elif isinstance(message, CommentMessage):
            return (1, message.comment.id)
        raise Exception
    return Stream(paginator, extractor)

def make_mentions_message_stream(client: Client) -> IStandardStreamEventSubject[CommentMessage]:
    it = client.p.message.pull.mentions()
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: x.comment.id)
