
from __future__ import annotations
from typing import Any, Mapping

from ..flair_emoji import FlairEmoji

def load_flair_emoji(d: Mapping[str, Any], name: str) -> FlairEmoji:
    return FlairEmoji(d, name)
