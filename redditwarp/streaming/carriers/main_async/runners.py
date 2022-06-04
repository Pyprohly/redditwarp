
from __future__ import annotations
from typing import TYPE_CHECKING, Awaitable, AsyncIterator, Optional, Union
if TYPE_CHECKING:
    from ....client_ASYNC import Client

import asyncio
from asyncio.queues import Queue
import inspect


def run(*streams: Union[Awaitable[None], AsyncIterator[float]], client: Optional[Client] = None) -> None:
    awbls = []
    aitrs = []
    for obj in streams:
        if inspect.isawaitable(obj):
            awbls.append(obj)
        else:
            if not isinstance(obj, AsyncIterator):
                raise Exception
            aitrs.append(obj)

    async def main() -> None:
        try:
            await asyncio.gather(
                _run_series_async(*aitrs),
                _run_parallel_async(*awbls),
            )
        finally:
            if client is not None:
                await client.close()

    asyncio.run(main())


async def _run_series_async(*streams: AsyncIterator[float], client: Optional[Client] = None) -> None:
    try:
        loop = asyncio.get_running_loop()

        q: Queue[AsyncIterator[float]] = Queue()
        count = 0
        for aitr in streams:
            count += 1
            q.put_nowait(aitr)

        while count > 0:
            aitr = await q.get()

            try:
                t = await aitr.__anext__()
            except StopAsyncIteration:
                count -= 1
            else:
                loop.call_later(t, (lambda: q.put_nowait(aitr)))

            q.task_done()

    finally:
        if client is not None:
            await client.close()

def run_series(*streams: AsyncIterator[float], client: Optional[Client] = None) -> None:
    async def main() -> None:
        await _run_series_async(*streams, client=client)
    asyncio.run(main())


async def _run_parallel_async(*streams: Awaitable[None], client: Optional[Client] = None) -> None:
    try:
        await asyncio.gather(*streams)
    finally:
        if client is not None:
            await client.close()

def run_parallel(*streams: Awaitable[None], client: Optional[Client] = None) -> None:
    async def main() -> None:
        await _run_parallel_async(*streams, client=client)
    asyncio.run(main())
