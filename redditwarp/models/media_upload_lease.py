
from typing import Mapping, Any

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
