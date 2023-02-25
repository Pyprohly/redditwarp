
from typing import Mapping, Any

from dataclasses import dataclass

from .datamemento import DatamementoDataclassesMixin

@dataclass(repr=False, eq=False)
class SubredditStyleAssetUploadLease(DatamementoDataclassesMixin):
    d: Mapping[str, Any]
    endpoint: str
    fields: Mapping[str, str]
    s3_object_key: str
    location: str
