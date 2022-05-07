
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .submission_collection_base import (
    BaseSubmissionCollectionDetails,
    GBaseSubmissionCollection,
)
from .submission_ASYNC import Submission
from ..model_loaders.submission_ASYNC import load_submission

class SubmissionCollectionDetails(BaseSubmissionCollectionDetails):
    def __init__(self, d: Mapping[str, Any], client: Client):
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


class SubmissionCollection(
    SubmissionCollectionDetails,
    GBaseSubmissionCollection[Submission],
):
    def _load_submission(self, m: Mapping[str, Any]) -> Submission:
        return load_submission(m, self.client)
