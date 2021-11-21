
from typing import Mapping, Any

from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class SubredditStyleAssetUploadLease(IArtifact):
    d: Mapping[str, Any]
    endpoint: str
    fields: Mapping[str, str]
    s3_object_key: str
    location: str
