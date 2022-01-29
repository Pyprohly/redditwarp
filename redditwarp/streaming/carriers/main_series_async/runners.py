
from __future__ import annotations
from typing import TYPE_CHECKING, Awaitable
if TYPE_CHECKING:
    from ....client_ASYNC import Client

import asyncio

def run(client: Client, *streams: Awaitable[None]) -> None:
    async def main() -> None:
        async with client:
            await asyncio.gather(*streams)
    asyncio.run(main())
