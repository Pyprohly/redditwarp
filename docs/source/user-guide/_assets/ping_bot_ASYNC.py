#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redditwarp.models.message_ASYNC import MailboxMessage

import asyncio

import redditwarp.ASYNC
from redditwarp.models.message_ASYNC import ComposedMessage
from redditwarp.streaming.makers.message_ASYNC import create_inbox_message_stream
from redditwarp.streaming.ASYNC import flow

async def main() -> None:
    client = redditwarp.ASYNC.Client.from_praw_config('SuvaBot')
    async with client:
        inbox_message_stream = create_inbox_message_stream(client)

        @inbox_message_stream.output.attach
        async def _(mesg: MailboxMessage) -> None:
            if isinstance(mesg, ComposedMessage):
                if mesg.subject.startswith('!ping'):
                    await client.p.message.send(
                        mesg.author_name,
                        're: ' + mesg.subject,
                        'pong',
                    )

        await flow(inbox_message_stream)

asyncio.run(main())
