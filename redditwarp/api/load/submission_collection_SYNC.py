
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...models.submission_collection_SYNC import SubmissionCollection, VisualSubmissionCollection

def load_submission_collection(d: Mapping[str, Any], client: Client) -> SubmissionCollection:
    return SubmissionCollection(d, client)

def load_visual_submission_collection(d: Mapping[str, Any], client: Client) -> VisualSubmissionCollection:
    return VisualSubmissionCollection(d, client)
