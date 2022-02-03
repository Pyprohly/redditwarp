
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Iterable
if TYPE_CHECKING:
    from ..client_ASYNC import Client
    from ..iterators.call_chunk_calling_async_iterator import CallChunkCallingAsyncIterator

from .custom_feed_base import BaseCustomFeed

class CustomFeed(BaseCustomFeed):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

    async def delete(self) -> None:
        await self.client.p.custom_feed.delete(self.owner, self.name)

    async def contains(self, sr_name: str) -> bool:
        return await self.client.p.custom_feed.contains(self.owner, self.name, sr_name)

    async def add_to(self, sr_name: str) -> None:
        await self.client.p.custom_feed.add_to(self.owner, self.name, sr_name)

    def bulk_add_to(self, sr_names: Iterable[str]) -> CallChunkCallingAsyncIterator[None]:
        return self.client.p.custom_feed.bulk_add_to(self.owner, self.name, sr_names)

    async def remove_from(self, sr_name: str) -> None:
        await self.client.p.custom_feed.remove_from(self.owner, self.name, sr_name)
