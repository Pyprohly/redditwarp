
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ...models.submission_collection_ASYNC import SubmissionCollection, PrimarySubmissionCollection

def load_submission_collection(d: Mapping[str, Any], client: Client) -> SubmissionCollection:
    return SubmissionCollection(d, client)

def load_primary_submission_collection(d: Mapping[str, Any], client: Client) -> PrimarySubmissionCollection:
    return PrimarySubmissionCollection(d, client)
