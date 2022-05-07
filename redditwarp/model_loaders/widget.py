
from __future__ import annotations
from typing import Mapping, Any

from ..models.widget import WidgetImageUploadLease

def load_widget_image_upload_lease(d: Mapping[str, Any]) -> WidgetImageUploadLease:
    lease_data = d['s3UploadLease']
    endpoint = f'https:{x}' if (x := lease_data['action']).startswith('//') else x
    fields = {field['name']: field['value'] for field in lease_data['fields']}
    s3_object_key = fields['key']
    return WidgetImageUploadLease(
        d=d,
        endpoint=endpoint,
        fields=fields,
        s3_object_key=s3_object_key,
        location=f"{endpoint}/{s3_object_key}",
    )
