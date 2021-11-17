
from __future__ import annotations
from typing import Mapping, Any

from dataclasses import dataclass

from ..artifact import IArtifact

@dataclass(repr=False, eq=False)
class WidgetImageUploadLease(IArtifact):
    d: Mapping[str, Any]
    endpoint: str
    fields: Mapping[str, str]
    s3_object_key: str
    location: str
