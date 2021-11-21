
from __future__ import annotations
from typing import Mapping, Any

from ..subreddit_style_asset_upload_lease import SubredditStyleAssetUploadLease

def load_subreddit_style_asset_upload_lease(d: Mapping[str, Any]) -> SubredditStyleAssetUploadLease:
    lease_data = d['s3UploadLease']
    endpoint = f'https:{x}' if (x := lease_data['action']).startswith('//') else x
    fields = {field['name']: field['value'] for field in lease_data['fields']}
    s3_object_key = fields['key']
    return SubredditStyleAssetUploadLease(
        d=d,
        endpoint=endpoint,
        fields=fields,
        s3_object_key=s3_object_key,
        location=f"{endpoint}/{s3_object_key}",
    )
