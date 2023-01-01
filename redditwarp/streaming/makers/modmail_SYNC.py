
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.modmail_SYNC import ConversationInfo, Message
    from ..stream_SYNC import IStandardStreamEventSubject

from ..stream_SYNC import Stream


def make_conversation_message_new_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    it = client.p.modmail.pull.new()
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: (x[0].id, x[1].id))

def make_conversation_message_join_request_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    it = client.p.modmail.pull.join_requests()
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: (x[0].id, x[1].id))
