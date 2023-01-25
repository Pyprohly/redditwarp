
from __future__ import annotations
from typing import TYPE_CHECKING, Union, overload
if TYPE_CHECKING:
    from ...models.modmail_ASYNC import ConversationInfo, Message
    from ..stream_ASYNC import IStandardStreamEventSubject
    from ...pagination.async_paginator import CursorAsyncPaginator

from ...client_ASYNC import Client
from ..stream_ASYNC import Stream


def get_conversation_message_new_stream_paginator(client: Client) -> CursorAsyncPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.new().get_paginator()

@overload
def make_conversation_message_new_stream(paginator: CursorAsyncPaginator[tuple[ConversationInfo, Message]], /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
@overload
def make_conversation_message_new_stream(client: Client, /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
def make_conversation_message_new_stream(arg: Union[CursorAsyncPaginator[tuple[ConversationInfo, Message]], Client]) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    paginator: CursorAsyncPaginator[tuple[ConversationInfo, Message]]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.modmail.pull.new().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: (x[0].id, x[1].id))


def get_conversation_message_join_request_stream_paginator(client: Client) -> CursorAsyncPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.join_requests().get_paginator()

@overload
def make_conversation_message_join_request_stream(paginator: CursorAsyncPaginator[tuple[ConversationInfo, Message]], /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
@overload
def make_conversation_message_join_request_stream(client: Client, /) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]: ...
def make_conversation_message_join_request_stream(arg: Union[CursorAsyncPaginator[tuple[ConversationInfo, Message]], Client]) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    paginator: CursorAsyncPaginator[tuple[ConversationInfo, Message]]
    if isinstance(arg, Client):
        client = arg
        paginator = client.p.modmail.pull.join_requests().get_paginator()
    else:
        paginator = arg
    return Stream(paginator, lambda x: (x[0].id, x[1].id))
