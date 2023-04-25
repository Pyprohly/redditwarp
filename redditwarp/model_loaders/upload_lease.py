
from __future__ import annotations
from typing import Mapping, Any

from ..models.upload_lease import UploadLease

def load_upload_lease(d: Mapping[str, Any]) -> UploadLease:
    lease_data = d['s3UploadLease']
    endpoint = f'https:{x}' if (x := lease_data['action']).startswith('//') else x
    fields = {field['name']: field['value'] for field in lease_data['fields']}
    s3_object_key = fields['key']
    return UploadLease(
        d=d,
        endpoint=endpoint,
        fields=fields,
        s3_object_key=s3_object_key,
        location=f"{endpoint}/{s3_object_key}",
    )
