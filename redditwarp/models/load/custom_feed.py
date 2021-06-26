
from __future__ import annotations
from typing import Any, Mapping

from ..custom_feed import CustomFeed

def load_custom_feed(d: Mapping[str, Any]) -> CustomFeed:
    return CustomFeed(d)
