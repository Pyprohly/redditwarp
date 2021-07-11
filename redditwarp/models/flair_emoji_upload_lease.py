
from typing import Mapping, Any

class FlairEmojiUploadLease:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d = d
        dd = d['s3UploadLease']
        self.bucket_url: str = 'https:' + dd['action']
        self.fields: Mapping[str, str] = {field['name']: field['value'] for field in dd['fields']}
