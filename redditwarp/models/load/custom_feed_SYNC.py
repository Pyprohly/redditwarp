
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..custom_feed_SYNC import CustomFeed

def load_custom_feed(d: Mapping[str, Any], client: Client) -> CustomFeed:
    return CustomFeed(d, client)
