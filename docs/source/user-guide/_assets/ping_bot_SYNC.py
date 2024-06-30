#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redditwarp.models.message_SYNC import MailboxMessage

import redditwarp.SYNC
from redditwarp.models.message_SYNC import ComposedMessage
from redditwarp.streaming.makers.message_SYNC import create_inbox_message_stream
from redditwarp.streaming.SYNC import flow

def main() -> None:
    client = redditwarp.SYNC.Client.from_praw_config('SuvaBot')
    with client:
        inbox_message_stream = create_inbox_message_stream(client)

        @inbox_message_stream.output.attach
        def _(mesg: MailboxMessage) -> None:
            if isinstance(mesg, ComposedMessage):
                if mesg.subject.startswith('!ping'):
                    client.p.message.send(
                        mesg.author_name,
                        're: ' + mesg.subject,
                        'pong',
                    )

        flow(inbox_message_stream)

main()
