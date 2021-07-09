
from typing import Mapping, Any

from ..flair_emoji_upload_lease import FlairEmojiUploadLease

def load_flair_emoji_upload_lease(d: Mapping[str, Any]) -> FlairEmojiUploadLease:
    return FlairEmojiUploadLease(d)
