
from __future__ import annotations
from typing import TYPE_CHECKING, Union, overload
if TYPE_CHECKING:
    from ...models.modmail_SYNC import ConversationInfo, Message
    from ..stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ...client_SYNC import Client
from ..stream_SYNC import Stream


def get_make_conversation_message_new_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.new().get_paginator()

@overload
def make_conversation_message_new_stream(paginator: CursorPaginator[tuple[ConversationInfo, Message]], /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
@overload
def make_conversation_message_new_stream(client: Client, /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
def make_conversation_message_new_stream(arg: Union[CursorPaginator[tuple[ConversationInfo, Message]], Client]) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    paginator: CursorPaginator[tuple[ConversationInfo, Message]]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.modmail.pull.new().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: (x[0].id, x[1].id))


def get_conversation_message_join_request_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.join_requests().get_paginator()

@overload
def make_conversation_message_join_request_stream(paginator: CursorPaginator[tuple[ConversationInfo, Message]], /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
@overload
def make_conversation_message_join_request_stream(client: Client, /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
def make_conversation_message_join_request_stream(arg: Union[CursorPaginator[tuple[ConversationInfo, Message]], Client]) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    paginator: CursorPaginator[tuple[ConversationInfo, Message]]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.modmail.pull.join_requests().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: (x[0].id, x[1].id))
