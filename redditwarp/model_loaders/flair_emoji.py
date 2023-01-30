
from __future__ import annotations
from typing import Mapping, Any

from ..models.flair_emoji import FlairEmojiUploadLease, FlairEmoji

def load_flair_emoji_upload_lease(d: Mapping[str, Any]) -> FlairEmojiUploadLease:
    lease_data = d['s3UploadLease']
    endpoint = f'https:{x}' if (x := lease_data['action']).startswith('//') else x
    fields = {field['name']: field['value'] for field in lease_data['fields']}
    s3_object_key = fields['key']
    return FlairEmojiUploadLease(
        d=d,
        endpoint=endpoint,
        fields=fields,
        s3_object_key=s3_object_key,
        location=f"{endpoint}/{s3_object_key}",
    )

def load_flair_emoji(d: Mapping[str, Any], name: str) -> FlairEmoji:
    full_id36: str = d['created_by']
    _, _, id36 = full_id36.partition('_')
    return FlairEmoji(
        d=d,
        name=name,
        creator_id36=id36,
        creator_id=int(id36, 36),
        image_url=d['url'],
        mod_only=d['mod_flair_only'],
        post_enabled=d['post_flair_allowed'],
        user_enabled=d['user_flair_allowed'],
    )
