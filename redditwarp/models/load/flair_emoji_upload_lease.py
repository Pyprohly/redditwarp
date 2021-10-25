
from typing import Mapping, Any

from ..flair_emoji_upload_lease import FlairEmojiUploadLease

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
        resource_location=f"{endpoint}/{s3_object_key}",
    )
