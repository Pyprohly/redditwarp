
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncIterator, Optional
if TYPE_CHECKING:
    from ..client_ASYNC import Client

import asyncio
from asyncio.queues import Queue


def run(*streams: AsyncIterator[float], client: Optional[Client] = None) -> None:
    run_parallel(*streams, client=client)

def run_series(*streams: AsyncIterator[float], client: Optional[Client] = None) -> None:
    async def main() -> None:
        try:
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

        finally:
            if client is not None:
                await client.close()

    asyncio.run(main())

def run_parallel(*streams: AsyncIterator[float], client: Optional[Client] = None) -> None:
    async def main() -> None:
        async def _coro_func(aitr: AsyncIterator[float]) -> None:
            async for t in aitr:
                await asyncio.sleep(t)

        awbls = (_coro_func(m) for m in streams)
        try:
            await asyncio.gather(*awbls)
        finally:
            if client is not None:
                await client.close()

    asyncio.run(main())
