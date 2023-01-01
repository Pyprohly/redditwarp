
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ..models.submission_collection_SYNC import SubmissionCollectionInfo, SubmissionCollection

def load_submission_collection_info(d: Mapping[str, Any], client: Client) -> SubmissionCollectionInfo:
    return SubmissionCollectionInfo(d, client)

def load_submission_collection(d: Mapping[str, Any], client: Client) -> SubmissionCollection:
    return SubmissionCollection(d, client)
