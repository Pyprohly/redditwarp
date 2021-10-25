
from typing import Mapping, Any

from ..media_upload_lease import MediaUploadLease

def load_media_upload_lease(d: Mapping[str, Any]) -> MediaUploadLease:
    lease_data = d['args']
    endpoint = f'https:{x}' if (x := lease_data['action']).startswith('//') else x
    fields = {field['name']: field['value'] for field in lease_data['fields']}
    s3_object_key = fields['key']
    asset = d['asset']
    return MediaUploadLease(
        d=d,
        endpoint=endpoint,
        fields=fields,
        s3_object_key=fields['key'],
        resource_location=f"{endpoint}/{s3_object_key}",
        media_id=asset['asset_id'],
        filename=asset['payload']['filepath'],
        websocket_url=asset['websocket_url'],
    )
