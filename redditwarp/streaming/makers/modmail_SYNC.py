
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.modmail_SYNC import ConversationInfo, Message
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ..stream_SYNC import Stream


def conversation_message_new_extractor(x: tuple[ConversationInfo, Message]) -> object:
    return (x[0].id, x[1].id)

def get_conversation_message_new_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.new().get_paginator()

def make_conversation_message_new_stream(paginator: CursorPaginator[tuple[ConversationInfo, Message]], past: Optional[Iterable[tuple[ConversationInfo, Message]]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return Stream(paginator, conversation_message_new_extractor, past=past, seen=seen)

def create_conversation_message_new_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_conversation_message_new_stream(get_conversation_message_new_stream_paginator(client))


def conversation_message_join_request_extractor(x: tuple[ConversationInfo, Message]) -> object:
    return (x[0].id, x[1].id)

def get_conversation_message_join_request_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.join_requests().get_paginator()

def make_conversation_message_join_request_stream(paginator: CursorPaginator[tuple[ConversationInfo, Message]], past: Optional[Iterable[tuple[ConversationInfo, Message]]] = None, seen: Optional[Iterable[object]] = None) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return Stream(paginator, conversation_message_join_request_extractor, past=past, seen=seen)

def create_conversation_message_join_request_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_conversation_message_join_request_stream(get_conversation_message_join_request_stream_paginator(client))
