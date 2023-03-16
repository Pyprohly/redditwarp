#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redditwarp.models.comment_ASYNC import Comment

import asyncio

import redditwarp.ASYNC
from redditwarp.streaming.makers.subreddit_ASYNC import create_comment_stream
from redditwarp.streaming.ASYNC import flow

sr = 'test'
user = 'test'
needle = 'Hello World'

async def main() -> None:
    client = redditwarp.ASYNC.Client.from_praw_config('SuvaBot')
    async with client:
        comment_stream = create_comment_stream(client, sr)

        @comment_stream.output.attach
        async def _(comm: Comment) -> None:
            if needle in comm.body:
                subject = f"World greeted by u/{comm.author_display_name}"
                body = comm.permalink
                await client.p.message.send(user, subject, body)

        await flow(comment_stream)

asyncio.run(main())
