
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .live_thread import LiveThread as BaseLiveThread, LiveUpdate as BaseLiveUpdate

class LiveThread(BaseLiveThread):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client

    def config(self,
        title: str,
        description: str,
        resources: str,
        nsfw: bool,
    ) -> None:
        self.client.p.live_thread.config(self.idt, title, description, resources, nsfw)

    def get_update(self, uuid: str) -> LiveUpdate:
        return self.client.p.live_thread.get_update(self.idt, uuid)

    def create_update(self, body: str) -> None:
        self.client.p.live_thread.create_update(self.idt, body)

    def strike_update(self, uuid: str) -> None:
        self.client.p.live_thread.strike_update(self.idt, uuid)

    def delete_update(self, uuid: str) -> None:
        self.client.p.live_thread.delete_update(self.idt, uuid)


class LiveUpdate(BaseLiveUpdate):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
