
from __future__ import annotations
from typing import Any, Mapping

from ..flair_emoji import FlairEmoji

def load_flair_emoji(d: Mapping[str, Any], name: str) -> FlairEmoji:
    full_id36: str = d['created_by']
    _, _, id36 = full_id36.partition('_')
    return FlairEmoji(
        d=d,
        name=name,
        creator_id36=id36,
        creator_id=int(id36, 36),
        image_url=d['url'],
        post_enabled=d['post_flair_allowed'],
        user_enabled=d['user_flair_allowed'],
        mod_only=d['mod_flair_only'],
    )
