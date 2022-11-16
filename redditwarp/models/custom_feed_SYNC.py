
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Iterable
if TYPE_CHECKING:
    from ..client_SYNC import Client
    from ..iterators.call_chunk_calling_iterator import CallChunkCallingIterator

from .custom_feed import CustomFeed as BaseCustomFeed

class CustomFeed(BaseCustomFeed):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

    def delete(self) -> None:
        self.client.p.custom_feed.delete(self.owner, self.name)

    def contains(self, sr_name: str) -> bool:
        return self.client.p.custom_feed.contains(self.owner, self.name, sr_name)

    def add_to(self, sr_name: str) -> None:
        self.client.p.custom_feed.add_to(self.owner, self.name, sr_name)

    def bulk_add_to(self, sr_names: Iterable[str]) -> CallChunkCallingIterator[None]:
        return self.client.p.custom_feed.bulk_add_to(self.owner, self.name, sr_names)

    def remove_from(self, sr_name: str) -> None:
        self.client.p.custom_feed.remove_from(self.owner, self.name, sr_name)
