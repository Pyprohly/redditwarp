
from __future__ import annotations
from typing import Mapping, Any

from ..models.flair_emoji import FlairEmoji

from .upload_lease import load_upload_lease as load_flair_emoji_upload_lease  # noqa: F401

def load_flair_emoji(d: Mapping[str, Any], name: str) -> FlairEmoji:
    full_id36: str = d['created_by']
    _, _, id36 = full_id36.partition('_')
    return FlairEmoji(
        d=d,
        name=name,
        image_url=d['url'],
        creator_idn=(creator_idn := int(id36, 36)),
        creator_id=creator_idn,
        creator_id36=id36,
        post_enabled=d['post_flair_allowed'],
        user_enabled=d['user_flair_allowed'],
        mod_only=d['mod_flair_only'],
    )
