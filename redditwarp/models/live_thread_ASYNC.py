
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .live_thread_base import BaseLiveThread, BaseLiveUpdate

class LiveThread(BaseLiveThread):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

    async def configure(self, title: str, description: str, resources: str, nsfw: bool) -> None:
        await self.client.p.live_thread.configure(self.idt, title, description, resources, nsfw)

    async def get_live_update(self, update_uuid: str) -> LiveUpdate:
        return await self.client.p.live_thread.get_live_update(self.idt, update_uuid)

    async def create_live_update(self, body: str) -> None:
        await self.client.p.live_thread.create_live_update(self.idt, body)

    async def strike_live_update(self, update_uuid: str) -> None:
        await self.client.p.live_thread.strike_live_update(self.idt, update_uuid)

    async def delete_live_update(self, update_uuid: str) -> None:
        await self.client.p.live_thread.delete_live_update(self.idt, update_uuid)


class LiveUpdate(BaseLiveUpdate):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client
