
from typing import Mapping, Any

from ..models.submission_media_upload_lease import SubmissionMediaUploadLease

def load_submission_media_upload_lease(d: Mapping[str, Any]) -> SubmissionMediaUploadLease:
    lease_data = d['args']
    endpoint = f'https:{x}' if (x := lease_data['action']).startswith('//') else x
    fields = {field['name']: field['value'] for field in lease_data['fields']}
    s3_object_key = fields['key']
    asset = d['asset']
    return SubmissionMediaUploadLease(
        d=d,
        endpoint=endpoint,
        fields=fields,
        s3_object_key=fields['key'],
        location=f"{endpoint}/{s3_object_key}",
        media_id=asset['asset_id'],
        declared_filepath=asset['payload']['filepath'],
        websocket_url=asset['websocket_url'],
    )
