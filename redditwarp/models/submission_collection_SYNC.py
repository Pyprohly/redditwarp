
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission_collection import (
    SubmissionCollectionInfo as BaseSubmissionCollectionInfo,
    SubmissionCollection as BaseSubmissionCollection,
)
from .submission_SYNC import Submission
from ..model_loaders.submission_SYNC import load_submission

class SubmissionCollectionInfo(BaseSubmissionCollectionInfo):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
        ("")

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

class SubmissionCollection(SubmissionCollectionInfo, BaseSubmissionCollection):
    @property
    def submissions(self) -> Sequence[Submission]:
        return self.__submissions

    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d, client)
        load = lambda d: load_submission(d, client)
        self.__submissions: Sequence[Submission] = self._load_submissions(d, load)
