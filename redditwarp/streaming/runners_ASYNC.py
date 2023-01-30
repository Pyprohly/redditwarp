
from __future__ import annotations
from typing import AsyncIterator

import asyncio
from asyncio.queues import Queue


async def flow(*streams: AsyncIterator[float]) -> None:
    await flow_parallel(*streams)

async def flow_series(*streams: AsyncIterator[float]) -> None:
    loop = asyncio.get_running_loop()

    aq: Queue[AsyncIterator[float]] = Queue()
    count = 0
    for aitr in streams:
        aq.put_nowait(aitr)
        count += 1

    while count > 0:
        aitr = await aq.get()

        try:
            t = await aitr.__anext__()
        except StopAsyncIteration:
            count -= 1
        else:
            loop.call_later(t, (lambda: aq.put_nowait(aitr)))

        aq.task_done()

async def flow_parallel(*streams: AsyncIterator[float]) -> None:
    async def coro_fn(aitr: AsyncIterator[float]) -> None:
        async for s in aitr:
            await asyncio.sleep(s)
    awbls = (coro_fn(m) for m in streams)
    await asyncio.gather(*awbls)
