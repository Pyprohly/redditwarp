
from typing import Mapping, Any

class MediaUploadLease:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d = d
        _args = d['args']
        self.bucket_url: str = 'https:' + _args['action']
        self.fields: Mapping[str, str] = {field['name']: field['value'] for field in _args['fields']}
        _asset = d['asset']
        self.asset_id: str = _asset['asset_id']
        self.filename: str = _asset['payload']['filepath']
        self.websocket_url: str = _asset['websocket_url']
