
from typing import Mapping, Any

class FlairEmojiUploadLease:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d = d
        self.bucket_url: str = 'https:' + d['action']
        self.fields: Mapping[str, str] = {field['name']: field['value'] for field in d['fields']}
