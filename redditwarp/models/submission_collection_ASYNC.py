
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .submission_collection import (
    SubmissionCollectionInfo as BaseSubmissionCollectionInfo,
    SubmissionCollection as BaseSubmissionCollection,
)
from .submission_ASYNC import Submission
from ..model_loaders.submission_ASYNC import load_submission

class SubmissionCollectionInfo(BaseSubmissionCollectionInfo):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client

    async def add_post(self, submission_id: int) -> None:
        await self.client.p.collection.add_post(self.uuid, submission_id)

    async def remove_post(self, submission_id: int) -> None:
        await self.client.p.collection.remove_post(self.uuid, submission_id)

    async def reorder(self, submission_ids: Sequence[int]) -> None:
        await self.client.p.collection.reorder(self.uuid, submission_ids)

    async def delete(self) -> None:
        await self.client.p.collection.delete(self.uuid)

    async def set_title(self, title: str) -> None:
        await self.client.p.collection.set_title(self.uuid, title)

    async def set_description(self, desc: str) -> None:
        await self.client.p.collection.set_description(self.uuid, desc)

class SubmissionCollection(SubmissionCollectionInfo, BaseSubmissionCollection):
    @property
    def submissions(self) -> Sequence[Submission]:
        return self.__submissions

    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d, client)
        load = lambda d: load_submission(d, client)
        self.__submissions: Sequence[Submission] = self._load_submissions(d, load)
