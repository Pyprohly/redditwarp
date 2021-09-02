
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .submission_collection_base import (
    BaseSubmissionCollectionDetails,
    GenericBaseSubmissionCollection,
)
from .submission_ASYNC import Submission
from .load.submission_ASYNC import load_submission

class SubmissionCollectionDetails(BaseSubmissionCollectionDetails):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class SubmissionCollection(
    SubmissionCollectionDetails,
    GenericBaseSubmissionCollection[Submission],
):
    def _load_submission(self, m: Mapping[str, Any]) -> Submission:
        return load_submission(m, self.client)
