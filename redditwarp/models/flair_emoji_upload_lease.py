
from typing import Mapping, Any

class FlairEmojiUploadLease:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d = d
        _lease_data = d['s3UploadLease']
        self.endpoint: str = 'https:' + _lease_data['action']
        self.fields: Mapping[str, str] = {field['name']: field['value'] for field in _lease_data['fields']}
        self.s3_object_key = self.fields['key']
        self.resource_location: str = f"{self.endpoint}/{self.s3_object_key}"
