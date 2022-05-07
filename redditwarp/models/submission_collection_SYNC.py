
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission_collection_base import (
    BaseSubmissionCollectionDetails,
    GBaseSubmissionCollection,
)
from .submission_SYNC import Submission
from ..model_loaders.submission_SYNC import load_submission

class SubmissionCollectionDetails(BaseSubmissionCollectionDetails):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

    def add_post(self, submission_id: int) -> None:
        self.client.p.collection.add_post(self.uuid, submission_id)

    def remove_post(self, submission_id: int) -> None:
        self.client.p.collection.remove_post(self.uuid, submission_id)

    def reorder(self, submission_ids: Sequence[int]) -> None:
        self.client.p.collection.reorder(self.uuid, submission_ids)

    def delete(self) -> None:
        self.client.p.collection.delete(self.uuid)

    def set_title(self, title: str) -> None:
        self.client.p.collection.set_title(self.uuid, title)

    def set_description(self, desc: str) -> None:
        self.client.p.collection.set_description(self.uuid, desc)


class SubmissionCollection(
    SubmissionCollectionDetails,
    GBaseSubmissionCollection[Submission],
):
    def _load_submission(self, m: Mapping[str, Any]) -> Submission:
        return load_submission(m, self.client)
