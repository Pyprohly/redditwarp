
from typing import Mapping, Any

from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class MediaUploadLease(IArtifact):
    d: Mapping[str, Any]
    endpoint: str
    fields: Mapping[str, str]
    s3_object_key: str
    location: str
    media_id: str
    declared_filepath: str
    websocket_url: str
