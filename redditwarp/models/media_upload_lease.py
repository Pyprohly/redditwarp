
from typing import Mapping, Any

class MediaUploadLease:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d = d
        _lease_data = d['args']
        self.endpoint: str = 'https:' + _lease_data['action']
        self.fields: Mapping[str, str] = {field['name']: field['value'] for field in _lease_data['fields']}
        self.s3_object_key = self.fields['key']
        self.resource_location: str = f"{self.endpoint}/{self.s3_object_key}"
        _asset = d['asset']
        self.media_id: str = _asset['asset_id']
        self.filename: str = _asset['payload']['filepath']
        self.websocket_url: str = _asset['websocket_url']
