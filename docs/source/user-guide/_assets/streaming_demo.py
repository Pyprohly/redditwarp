#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redditwarp.models.submission_ASYNC import Submission
    from redditwarp.models.comment_ASYNC import Comment

import sys
import asyncio
import traceback

import redditwarp.ASYNC
from redditwarp.streaming.makers.subreddit_ASYNC import (
    create_submission_stream,
    create_comment_stream,
)
from redditwarp.streaming.ASYNC import flow
from redditwarp.util.passthru import passthru

async def main() -> None:
    client = redditwarp.ASYNC.Client()
    async with client:
        submission_stream = create_submission_stream(client, 'AskReddit')

        @submission_stream.output.attach
        async def _(subm: Submission) -> None:
            print(f"{subm.id36}+", '*', repr(subm.title))

        comment_stream = create_comment_stream(client, 'AskReddit')

        @comment_stream.output.attach
        async def _(comm: Comment) -> None:
            print(f"+{comm.id36}", '-', repr(comm.body)[:20])

        @passthru(comment_stream.error.attach)
        @passthru(submission_stream.error.attach)
        async def _(exc: Exception) -> None:
            print('<>', file=sys.stderr)
            traceback.print_exception(exc.__class__, exc, exc.__traceback__)
            print('</>', file=sys.stderr)

        await flow(
            submission_stream,
            comment_stream,
        )

asyncio.run(main())
