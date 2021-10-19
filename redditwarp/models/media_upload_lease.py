
from typing import Mapping, Any

import sys
from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class MediaUploadLease(IArtifact):
    d: Mapping[str, Any]
    endpoint: str
    fields: Mapping[str, str]
    s3_object_key: str
    resource_location: str
    media_id: str
    filename: str
    websocket_url: str

    if sys.version_info[:3] == (3, 9, 7):
        # https://bugs.python.org/issue45081
        def __init__(self,
            d: Mapping[str, Any],
            endpoint: str,
            fields: Mapping[str, str],
            s3_object_key: str,
            resource_location: str,
            media_id: str,
            filename: str,
            websocket_url: str,
        ) -> None:
            self.d = d
            self.endpoint = endpoint
            self.fields = fields
            self.s3_object_key = s3_object_key
            self.resource_location = resource_location
            self.media_id = media_id
            self.filename = filename
            self.websocket_url = websocket_url
