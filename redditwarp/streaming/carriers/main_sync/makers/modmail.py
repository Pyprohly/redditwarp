
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....client_SYNC import Client
    from .....models.modmail_SYNC import Conversation, Message
    from ..stream import IStandardStreamEventSubject

from ..stream import Stream


def make_conversation_and_message_stream(client: Client) -> IStandardStreamEventSubject[tuple[Conversation, Message]]:
    it = client.p.modmail.conversation.pulls.new()
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: (x[0].id, x[1].id))
